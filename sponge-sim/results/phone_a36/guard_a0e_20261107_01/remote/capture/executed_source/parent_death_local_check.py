"""Linux engineering checks with sleeping own children, no device/load/timing.

Parent-exit and parent-SIGKILL fixtures bypass Python cleanup deliberately.
Only this check process becomes a child subreaper, to reap its own orphans;
the original setting is restored. All files are in a NEW caller output path.
This does not validate arbitrary descendants or Android/proot behavior.
"""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import time

from posix_runtime import OwnGroup, stop_group, write_new_json


def control(option, value):
    libc = ctypes.CDLL(None, use_errno=True)
    prctl = libc.prctl
    prctl.restype = ctypes.c_int
    prctl.argtypes = [ctypes.c_int, *([ctypes.c_ulong]*4)]
    if prctl(option, value, 0, 0, 0):
        raise OSError(ctypes.get_errno(), 'local fixture prctl failed')


def flag(option):
    value = ctypes.c_int()
    control(option, ctypes.addressof(value))
    return value.value


def line(process):
    if not select.select([process.stdout], [], [], 10)[0]:
        raise TimeoutError('fixture stdout readiness deadline')
    raw = os.read(process.stdout.fileno(), 4096)
    return json.loads(raw)


def wait_adopted(pid):
    deadline = time.monotonic()+5
    while True:
        waited, status = os.waitpid(pid, os.WNOHANG)
        if waited:
            return os.waitstatus_to_exitcode(status)
        if time.monotonic() >= deadline:
            raise TimeoutError('direct adopted fixture did not exit')
        time.sleep(.01)


def payload():
    result = dict(pid=os.getpid(), ppid=os.getppid(), pgid=os.getpgrp(),
                  parent_death_signal=flag(2), torch_imported='torch' in sys.modules)
    if '--ignore-term' in sys.argv:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
    print(json.dumps(result), flush=True)
    time.sleep(60)


def creator(root):
    child = OwnGroup([sys.executable, str(Path(__file__).resolve()), '--payload'], root,
                     stdout=subprocess.PIPE)
    write_new_json(root/'owned_child.json', dict(pid=child.process.pid, pgid=child.pgid))
    ready = line(child.process)
    write_new_json(root/'child_ready.json', ready)
    print(json.dumps(ready), flush=True)
    if sys.stdin.buffer.read(1) != b'X':
        raise RuntimeError('fixture handoff missing')
    os._exit(23)  # no context manager, finally, atexit or stop_group


def main(root):
    if sys.platform != 'linux':
        raise RuntimeError('local Linux engineering check only')
    root = Path(root).resolve(); root.mkdir(parents=True, exist_ok=False)
    source = Path(__file__).resolve().parent
    snapshots = root/'executed_source'; snapshots.mkdir()
    hashes = {}
    for name in ('checks.py', 'linux_observe.py', 'posix_runtime.py', Path(__file__).name):
        data = (source/name).read_bytes()
        with (snapshots/name).open('xb') as f:
            f.write(data)
        hashes[name] = hashlib.sha256(data).hexdigest()
    receipt = dict(status='INCOMPLETE', scope='LOCAL_LINUX_SLEEPING_DIRECT_CHILD_ONLY',
                   source_sha256=hashes, checks={}, cases=[], device_qualified=False)
    original = flag(37)  # PR_GET_CHILD_SUBREAPER
    control(36, 1)  # PR_SET_CHILD_SUBREAPER, THIS process only
    try:
        for mode in ('parent_exit', 'parent_SIGKILL'):
            case = root/mode; case.mkdir()
            with (case/'creator.stderr').open('xb') as stderr:
                parent = subprocess.Popen([sys.executable, str(Path(__file__).resolve()),
                                           '--creator', str(case)], cwd=root,
                                          stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                          stderr=stderr, start_new_session=True)
                child_pid = None; reaped = False
                try:
                    ready = line(parent); child_pid = ready['pid']
                    assert ready['parent_death_signal'] == signal.SIGKILL
                    assert ready['ppid'] == parent.pid and ready['pgid'] == child_pid
                    assert not ready['torch_imported']
                    if mode == 'parent_exit':
                        parent.stdin.write(b'X'); parent.stdin.flush()
                        assert parent.wait(timeout=5) == 23
                    else:
                        parent.kill()
                        assert parent.wait(timeout=5) == -signal.SIGKILL
                    code = wait_adopted(child_pid); reaped = True
                    assert code == -signal.SIGKILL
                    receipt['cases'].append(dict(mode=mode, child=ready, child_exit=code,
                                                 parent_exit=parent.returncode, reaped=True))
                    receipt['checks'][mode+'_kills_direct_child_after_exec'] = True
                finally:
                    if parent.poll() is None:
                        parent.kill(); parent.wait(timeout=5)
                    if child_pid is None and (case/'owned_child.json').exists():
                        child_pid = json.loads((case/'owned_child.json').read_bytes())['pid']
                    if child_pid is not None and not reaped:
                        try:
                            os.killpg(child_pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                        wait_adopted(child_pid)
                    parent.stdin.close(); parent.stdout.close()
        child = OwnGroup([sys.executable, str(Path(__file__).resolve()), '--payload',
                          '--ignore-term'], root, stdout=subprocess.PIPE)
        try:
            ready = line(child.process)
            assert ready['parent_death_signal'] == signal.SIGKILL
            stop_group(child, grace_s=.2)
            assert child.process.returncode == -signal.SIGKILL and not child.group_live()
            receipt['checks']['ordinary_TERM_KILL_reap_still_works'] = True
        finally:
            stop_group(child); child.process.stdout.close()
        assert 'torch' not in sys.modules
        receipt['checks']['no_Torch_import_or_device_access'] = True
        assert all(hashlib.sha256((source/n).read_bytes()).hexdigest() == h for n,h in hashes.items())
        receipt['checks']['executed_sources_unchanged'] = True
        receipt['status'] = 'LOCAL_ENGINEERING_PASS_NOT_DEVICE_QUALIFIED'
    except BaseException as e:
        receipt.update(status='FAILED', error=type(e).__name__, message=str(e))
        raise
    finally:
        control(36, original)
        receipt['subreaper_restored'] = flag(37) == original
        write_new_json(root/'receipt.json', receipt)
        print(receipt['status'], receipt['checks'], flush=True)


if __name__ == '__main__':
    if sys.argv[1] == '--payload':
        payload()
    elif sys.argv[1] == '--creator':
        creator(Path(sys.argv[2]))
    else:
        main(Path(sys.argv[1]))
