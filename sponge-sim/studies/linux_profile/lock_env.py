"""Set and restore one CPUFreq policy and its SMT siblings on Linux."""

import argparse
import fcntl
import json
import os
import signal
import subprocess
import time
from pathlib import Path


CPU_ROOT = Path('/sys/devices/system/cpu')
STATE_DIR = Path('/run/sponge-cpu-lock')


def read(path):
    return path.read_text().strip()


def set_value(path, value):
    if read(path) != value:
        path.write_text(value + '\n')
    # CPUFreq applies constraint updates from a workqueue.
    deadline = time.monotonic() + 3
    while (actual := read(path)) != value:
        if time.monotonic() >= deadline:
            raise RuntimeError(f'{path}: requested {value}, read back {actual}')
        time.sleep(0.05)


def cpu_list(text):
    cpus = set()
    for part in text.replace(',', ' ').split():
        start, dash, end = part.partition('-')
        if not start.isascii() or not start.isdecimal() or (dash and not (end.isascii() and end.isdecimal())):
            raise ValueError(f'invalid CPU list: {text!r}')
        lo, hi = int(start), int(end or start)
        if lo > hi:
            raise ValueError(f'invalid CPU list: {text!r}')
        cpus.update(range(lo, hi + 1))
    return cpus


def set_limits(policy, low, high):
    minimum = policy / 'scaling_min_freq'
    maximum = policy / 'scaling_max_freq'
    if int(low) > int(read(maximum)):
        set_value(maximum, high)
        set_value(minimum, low)
    else:
        set_value(minimum, low)
        set_value(maximum, high)
    if (read(minimum), read(maximum)) != (low, high):
        raise RuntimeError('CPUFreq limits changed after setting the policy')


def snapshot_policy(policy):
    epp = policy / 'energy_performance_preference'
    boost = policy / 'boost'
    return dict(policy=str(policy), governor=read(policy / 'scaling_governor'),
                low=read(policy / 'scaling_min_freq'), high=read(policy / 'scaling_max_freq'),
                epp=read(epp) if epp.is_file() else None,
                boost=read(boost) if boost.is_file() else None)


def snapshot(cpu, global_boost=False):
    target = CPU_ROOT / f'cpu{cpu}'
    siblings = cpu_list(read(target / 'topology/thread_siblings_list'))
    if cpu == 0 or cpu not in siblings or 0 in siblings:
        raise RuntimeError('choose a non-boot physical core with readable SMT topology')
    if cpu not in cpu_list(read(CPU_ROOT / 'online')):
        raise RuntimeError(f'CPU {cpu} is offline')
    policy = (target / 'cpufreq').resolve(strict=True)
    if not cpu_list(read(policy / 'related_cpus')) <= siblings:
        raise RuntimeError(f'{policy.name} also controls CPUs outside the target core')
    if 'performance' not in read(policy / 'scaling_available_governors').split():
        raise RuntimeError('performance governor is unavailable')

    # Prefer the per-policy AMD control so other cores keep their current boost.
    controls = (
        (policy / 'boost', '0'),
        (CPU_ROOT / 'intel_pstate/no_turbo', '1'),
        (CPU_ROOT / 'cpufreq/boost', '0'),
    )
    if global_boost:
        controls = controls[1:]
    for boost_path, boost_off in controls:
        if boost_path.is_file():
            boost_before = read(boost_path)
            if boost_before not in ('0', '1'):
                raise RuntimeError(f'unrecognized boost value in {boost_path}')
            break
    else:
        raise RuntimeError('no supported boost or turbo control found')

    online = {str(CPU_ROOT / f'cpu{s}/online'): read(CPU_ROOT / f'cpu{s}/online')
              for s in sorted(siblings - {cpu})}
    if any(value not in ('0', '1') for value in online.values()):
        raise RuntimeError('unrecognized SMT online state')
    if boost_path.parent != policy:
        policies = set((CPU_ROOT / 'cpufreq').glob('policy*'))
    else:
        policies = {policy}
        for path, value in online.items():
            if value == '1':
                policies.add((Path(path).parent / 'cpufreq').resolve(strict=True))
    return dict(cpu=cpu, policy=str(policy), boost_path=str(boost_path),
                boost_before=boost_before, boost_off=boost_off, online=online,
                policies=[snapshot_policy(p) for p in sorted(policies)])


def restore(state):
    set_value(Path(state['boost_path']), state['boost_before'])
    for path, value in state['online'].items():
        set_value(Path(path), value)
    for original in state['policies']:
        policy = Path(original['policy'])
        if original['boost'] is not None:
            set_value(policy / 'boost', original['boost'])
        set_value(policy / 'scaling_governor', original['governor'])
        set_limits(policy, original['low'], original['high'])
        if original['epp'] is not None:
            set_value(policy / 'energy_performance_preference', original['epp'])


def lock(state, frequency):
    policy = Path(state['policy'])
    set_value(Path(state['boost_path']), state['boost_off'])
    minimum = int(read(policy / 'cpuinfo_min_freq'))
    maximum = int(read(policy / 'cpuinfo_max_freq'))
    if not minimum <= frequency <= maximum:
        raise RuntimeError(f'{frequency} kHz is outside the non-boost range {minimum}–{maximum} kHz')
    for path in state['online']:
        set_value(Path(path), '0')
    if cpu_list(read(policy / 'affected_cpus')) != {state['cpu']}:
        raise RuntimeError('the policy still affects CPUs other than the selected CPU')
    set_value(policy / 'scaling_governor', 'performance')
    set_limits(policy, str(frequency), str(frequency))


def check_config(state, frequency):
    policy = Path(state['policy'])
    if (read(policy / 'scaling_governor'), read(policy / 'scaling_min_freq'),
            read(policy / 'scaling_max_freq')) != ('performance', str(frequency), str(frequency)):
        raise RuntimeError('CPUFreq governor or limits changed')
    if (read(Path(state['boost_path'])) != state['boost_off']
            or any(read(Path(path)) != '0' for path in state['online'])
            or cpu_list(read(policy / 'affected_cpus')) != {state['cpu']}):
        raise RuntimeError('boost, SMT or affected CPUs changed')


def verify(state, seconds):
    cpu = str(state['cpu'])
    frequency = state['frequency_khz']
    check_config(state, frequency)
    monitor = ['turbostat', '--quiet', '--cpu', cpu, '--show', 'CPU,Busy%,Bzy_MHz',
               '--interval', '1', '--num_iterations', str(seconds)]
    with subprocess.Popen(['taskset', '-c', cpu, 'sha256sum', '/dev/zero'],
                          stdout=subprocess.DEVNULL) as load:
        try:
            report = subprocess.run(monitor, timeout=seconds + 10, text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        finally:
            load.terminate()
    if report.returncode:
        raise RuntimeError(f'turbostat failed: {report.stdout.strip()}')
    samples = [tuple(map(float, row[1:])) for line in report.stdout.splitlines()
               if len(row := line.split()) == 3 and row[0] == cpu]
    if len(samples) != seconds or any(busy < 95 for busy, _ in samples):
        raise RuntimeError(f'expected {seconds} turbostat samples with CPU {cpu} at ≥95% busy; '
                           f'got {len(samples)} samples: {samples}')
    check_config(state, frequency)
    observed = [mhz for _, mhz in samples]
    target_mhz = frequency / 1000
    result = dict(cpu=state['cpu'], target_khz=frequency, samples=len(samples),
                  min_busy_pct=min(busy for busy, _ in samples),
                  min_bzy_mhz=min(observed), max_bzy_mhz=max(observed), tolerance_pct=1)
    print(json.dumps(result), flush=True)
    if any(not (0.99 * target_mhz <= mhz <= 1.01 * target_mhz) for mhz in observed):
        raise RuntimeError('effective frequency exceeds the ±1% tolerance')


def interrupted(signum, _frame):
    raise InterruptedError(f'received signal {signum}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='mode', required=True)
    for mode in ('lock', 'verify', 'unlock'):
        command = commands.add_parser(mode)
        command.add_argument('cpu', type=int)
        if mode == 'lock':
            command.add_argument('frequency_khz', type=int)
            command.add_argument('--global-boost', action='store_true',
                                 help='disable boost system-wide instead of using per-policy control')
        if mode != 'unlock':
            command.add_argument('--seconds', type=int, choices=range(3, 121), default=20,
                                 metavar='3..120', help='seconds of turbostat sampling (default: 20)')
    args = parser.parse_args()
    if os.geteuid() != 0:
        parser.error('run as root')
    if args.cpu < 0 or (args.mode == 'lock' and args.frequency_khz <= 0):
        parser.error('CPU and frequency must be valid nonnegative CPU / positive kHz values')

    for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
        signal.signal(signum, interrupted)
    STATE_DIR.mkdir(mode=0o700, exist_ok=True)
    saved = STATE_DIR / 'original.json'
    with (STATE_DIR / 'lock').open('a') as mutex:
        fcntl.flock(mutex, fcntl.LOCK_EX)
        if args.mode != 'lock':
            state = json.loads(read(saved))
            if state['cpu'] != args.cpu:
                parser.error(f"the saved lock belongs to CPU {state['cpu']}")
            if args.mode == 'verify':
                verify(state, args.seconds)
                return
            restore(state)
            saved.unlink()
            print(f'CPU {args.cpu}: original settings restored')
            return
        if saved.exists():
            parser.error(f'an active lock or incomplete rollback already exists in {saved}')
        state = snapshot(args.cpu, args.global_boost)
        state['frequency_khz'] = args.frequency_khz
        pending = saved.with_suffix('.tmp')
        pending.write_text(json.dumps(state) + '\n')
        pending.replace(saved)
        try:
            lock(state, args.frequency_khz)
            verify(state, args.seconds)
        except BaseException as lock_error:
            try:
                restore(state)
                saved.unlink()
            except Exception as error:
                raise RuntimeError(
                    f'lock failed: {lock_error}; rollback incomplete: {error}; saved state: {saved}'
                ) from error
            raise
        print(f'CPU {args.cpu}: effective frequency verified at {args.frequency_khz} kHz (±1%)')
        print(f'Original settings saved in {saved}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        raise SystemExit(f'CPU lock: {error}')
