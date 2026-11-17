"""Bounded own-child adapters. Local engineering validation only, not ARM-ready.

No Torch workload or experiment entry point. Android/proot group ownership,
sensor permissions, reaction bounds and overhead still need registered device
QA. Per-call helper startup overhead must be included in future controls.
"""
from dataclasses import asdict
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from checks import Reading
from linux_observe import sensor_frame


def bind_parent_death(expected_parent):
    """Linux direct-child SIGKILL on creator-thread death, before payload exec.

    Check parent identity on BOTH sides of prctl and verify the signal. Never
    fall back when unsupported. Ordinary same-credential exec preserves this
    setting; forked descendants do NOT inherit it. This is not protection for
    an arbitrary process tree, a stalled parent or Android/proot qualification.
    """
    if sys.platform != 'linux':
        raise RuntimeError('Linux parent-death support required')
    if type(expected_parent) is not int or expected_parent <= 1:
        raise ValueError('captured creating parent PID required')
    if os.getppid() != expected_parent:
        raise RuntimeError('creating parent changed before parent-death setup')
    import ctypes
    libc = ctypes.CDLL(None, use_errno=True)
    prctl = libc.prctl
    prctl.restype = ctypes.c_int
    prctl.argtypes = [ctypes.c_int, *([ctypes.c_ulong]*4)]
    if prctl(1, signal.SIGKILL, 0, 0, 0) != 0:  # PR_SET_PDEATHSIG
        raise OSError(ctypes.get_errno(), 'PR_SET_PDEATHSIG failed')
    actual = ctypes.c_int()
    if prctl(2, ctypes.addressof(actual), 0, 0, 0) != 0:  # PR_GET_PDEATHSIG
        raise OSError(ctypes.get_errno(), 'PR_GET_PDEATHSIG failed')
    if actual.value != signal.SIGKILL or os.getppid() != expected_parent:
        raise RuntimeError('parent-death readback or creating parent changed')


def positive(value):
    if isinstance(value,bool) or not math.isfinite(value) or value<=0:
        raise ValueError('positive finite timeout required')
    return value


class OwnGroup:
    """A new session containing only this new child and its descendants.

    A completed leader with a still-live group is NOT reported completed.
    TERM/KILL address this owned PGID, never a process name or a caller PID.
    A Linux bootstrap arms/verifies direct-child parent-death SIGKILL before
    exec. All helpers/workers use it; it adds startup cost to their deadlines.
    Only the direct child can be reaped here; forked descendants do not inherit
    the death signal. Unresolved descendants still invalidate cleanup. No PID
    lookup or attachment to pre-existing processes is allowed.
    """
    def __init__(self,args,cwd,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT):
        if sys.platform!='linux':
            raise RuntimeError('Linux-only adapter; no unguarded process fallback')
        if not isinstance(args,(list,tuple)) or not args:
            raise ValueError('nonempty explicit argument vector required')
        command=[sys.executable,str(Path(__file__).resolve()),'--exec-bound',str(os.getpid()),
                 *map(os.fspath,args)]
        self.process=subprocess.Popen(command,cwd=cwd,stdin=stdin,stdout=stdout,stderr=stderr,start_new_session=True)
        self.pgid=self.process.pid
        self.gone=False

    def group_live(self):
        if self.gone:return False
        try:
            os.killpg(self.pgid,0)
        except ProcessLookupError:
            self.gone=True
        return not self.gone

    def poll(self):
        code=self.process.poll()
        if code is not None and self.group_live():
            raise RuntimeError('leader exited while owned group members remain')
        return code

    def send(self,sig):
        if self.group_live():
            try:os.killpg(self.pgid,sig)
            except ProcessLookupError:self.gone=True

    def terminate(self):self.send(signal.SIGTERM)

    def kill(self):self.send(signal.SIGKILL)

    def wait(self,timeout):
        deadline=time.monotonic()+positive(timeout)
        try:self.process.wait(timeout=timeout)
        except subprocess.TimeoutExpired as e:raise TimeoutError('leader did not exit') from e
        while self.group_live():
            if time.monotonic()>=deadline:
                raise TimeoutError('owned group still exists after leader exit')
            time.sleep(.01)
        return self.process.returncode


def stop_group(child,grace_s=2):
    grace_s=positive(grace_s)
    child.terminate()
    try:child.wait(grace_s)
    except TimeoutError:
        child.kill()
        child.wait(grace_s)


def helper(mode,arguments,payload,cwd,timeout_s):
    """Bounded communicate includes stdin, reader/logger and helper exit.

    On any timeout/parse/worker error, cleanup occurs before propagating the
    exception to the supervisor, which then stops its measurement worker.
    """
    timeout_s=positive(timeout_s)
    data=json.dumps(payload,allow_nan=False).encode()
    if len(data)>65536:raise ValueError('helper request exceeds 64KiB')
    child=OwnGroup([sys.executable,str(Path(__file__).resolve()),mode,*map(str,arguments)],
                   cwd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        out,err=child.process.communicate(data,timeout=timeout_s)
        if child.poll() is None:
            raise RuntimeError('helper leader exited leaving group members')
        if child.process.returncode:
            raise RuntimeError('helper failed: '+err.decode(errors='replace')[-2000:])
        return json.loads(out)
    except BaseException:
        stop_group(child)
        raise
    finally:
        for stream in (child.process.stdin,child.process.stdout,child.process.stderr):
            if stream is not None:stream.close()


class BoundedSensors:
    """Every completed frame (valid or invalid) is durably captured before ACK.

    A timeout can leave a sequence gap/partial file; neither is retried or
    overwritten. A failed reader is poisoned for the remainder of the session.
    The read deadline includes capture/fsync, not just reading sensor files.
    """
    def __init__(self,config_path,config_sha256,cwd,timeout_s,capture_directory):
        self.config_path=Path(config_path).resolve();self.sha=config_sha256
        self.cwd=Path(cwd).resolve();self.timeout_s=positive(timeout_s)
        self.directory=Path(capture_directory).resolve()
        if not self.directory.is_relative_to(self.cwd):
            raise ValueError('capture directory must stay inside work directory')
        self.directory.mkdir(parents=True,exist_ok=False)
        self.last_frame=None;self.sequence=0;self.failed=False

    def read(self):
        if self.failed:raise RuntimeError('sensor reader invalid after previous failure; new session required')
        self.sequence+=1;self.last_frame=None
        target=self.directory/f'{self.sequence:06d}.json'
        try:
            response=helper('--sensor',[self.config_path,self.sha,target],dict(sequence=self.sequence),
                            self.cwd,self.timeout_s)
            frame=response['frame'];self.last_frame=frame
            captured=dict(sequence=self.sequence,config_sha256=self.sha,frame=frame)
            if response['capture_sha256']!=json_sha(captured):
                raise RuntimeError('sensor capture ACK/hash mismatch')
            if frame['errors'] or frame['reading'] is None:
                raise RuntimeError('invalid sensor frame: '+json.dumps(frame['errors']))
            return Reading(**frame['reading'])
        except BaseException:
            self.failed=True
            raise


class BoundedEvents:
    """One exclusive event file per ACK; partial files are retained on failure.

    fsync occurs in a helper with a deadline, never in the parent/worker. A
    missing ACK invalidates the session even if a partial event is present.
    """
    def __init__(self,directory,cwd,timeout_s):
        self.directory=Path(directory).resolve();self.cwd=Path(cwd).resolve()
        if not self.directory.is_relative_to(self.cwd):
            raise ValueError('event directory must stay inside work directory')
        self.timeout_s=positive(timeout_s);self.sequence=0
        self.directory.mkdir(parents=True,exist_ok=False)

    def emit(self,event):
        self.sequence+=1
        target=self.directory/f'{self.sequence:06d}.json'
        expected=dict(sequence=self.sequence,event=event)
        ack=helper('--event',[target],expected,self.cwd,self.timeout_s)
        if ack!={'sha256':json_sha(expected)}:
            raise RuntimeError('event ACK/hash mismatch')


def json_bytes(value):return (json.dumps(value,allow_nan=False)+'\n').encode()


def json_sha(value):return hashlib.sha256(json_bytes(value)).hexdigest()


def write_new_json(path,value):
    data=json_bytes(value)
    with Path(path).open('xb') as f:
        f.write(data);f.flush();os.fsync(f.fileno())
    return hashlib.sha256(data).hexdigest()


def bounded_text(path):
    with Path(path).open() as f:value=f.read(4097)
    if len(value)>4096:raise ValueError('sensor value exceeds 4KiB')
    return value


def internal_main():
    if len(sys.argv)>1 and sys.argv[1]=='--exec-bound':
        if len(sys.argv)<4:raise ValueError('parent PID and explicit command required')
        bind_parent_death(int(sys.argv[2]))
        os.execvp(sys.argv[3],sys.argv[3:])
        raise RuntimeError('exec unexpectedly returned')
    request=sys.stdin.buffer.read(65537)
    if len(request)>65536:raise ValueError('request exceeds 64KiB')
    payload=json.loads(request)
    if sys.argv[1]=='--sensor':
        path=Path(sys.argv[2])
        with path.open('rb') as f:config=f.read(65537)
        if len(config)>65536 or hashlib.sha256(config).hexdigest()!=sys.argv[3]:
            raise ValueError('sensor config size/hash changed')
        frame=sensor_frame(json.loads(config),read_text=bounded_text)
        if frame['reading'] is not None:frame['reading']=asdict(frame['reading'])
        captured=dict(sequence=payload['sequence'],config_sha256=sys.argv[3],frame=frame)
        result=dict(frame=frame,capture_sha256=write_new_json(sys.argv[4],captured))
    elif sys.argv[1]=='--event':
        result=dict(sha256=write_new_json(sys.argv[2],payload))
    else:raise ValueError('internal helper mode required')
    print(json.dumps(result,allow_nan=False),flush=True)


if __name__=='__main__':internal_main()
