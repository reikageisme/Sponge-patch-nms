"""Independently check saved native inventory identities/units/availability.

No device access, imported observer, Torch computation or performance inference.
"""
from pathlib import Path
import hashlib
import json
import subprocess

B = Path(__file__).resolve().parent
ROOT = B.parents[2]
SOURCE = ROOT/'sponge-sim/studies/pi3b_nms_observer_20261115'


def load(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    reg = load(SOURCE/'qa_config.json')
    result = load(B/'original/qa_result_01.json')
    manifest = load(B/'original/qa_manifest.json')
    receipt = load(B/'verification.json')
    assert result['status'] == receipt['status'] == 'PASS_SERVICE_POOL_INVENTORY_API_ONLY'
    assert manifest == load(B/'qa_manifest.json')
    assert manifest['tag'] == reg['tag'] == result['tag']
    assert manifest['commit'] == result['commit']
    assert result['config_sha256'] == manifest['config_sha256'] == sha(SOURCE/'qa_config.json')
    for name, digest in reg['source_sha256'].items():
        assert sha(SOURCE/name) == digest
        blob = subprocess.check_output(['git', 'show', f"{manifest['commit']}:sponge-sim/studies/pi3b_nms_observer_20261115/{name}"], cwd=ROOT)
        assert hashlib.sha256(blob).hexdigest() == digest
    for name, item in receipt['original_files'].items():
        assert sha(B/'original'/name) == item['sha256'] and (B/'original'/name).stat().st_size == item['bytes']
    before_remote = json.loads(load(B/'terminal_before_fetch.json')['stdout'])
    after_remote = json.loads(load(B/'terminal_after_fetch.json')['stdout'])
    assert before_remote['files'] == after_remote['files'] == receipt['original_files']
    assert before_remote['source_sha256'] == after_remote['source_sha256'] == reg['source_sha256']
    actual = load(B/'device_invocation.json')
    assert actual['returncode'] == 0 and json.loads(actual['stdout'])['unit_returncode'] == 0
    assert result['before_context'] == result['after_context']
    assert result['torch_configuration']['threads'] == 4 and result['torch_configuration']['interop'] == 1
    assert result['functional_check'] == dict(shape=[512, 512], operations=1, all_entries_equal=512, exact_pass=True)
    table = []
    for key in ('pre_import_inventory', 'pool_before', 'pool_after'):
        s = result[key]
        assert s['complete_stable_set'] and s['cgroup_path'] == reg['expected_cgroup']
        assert s['tids_before'] == s['tids_after'] == sorted(int(t) for t in s['threads'])
        assert s['pid'] in s['tids_before']
        for tid, x in s['threads'].items():
            assert x['status'] == 'OK' and x['affinity'] == [0, 1, 2, 3]
            assert x['stat']['start_ticks'] == s['end_start_ticks'][tid]['start_ticks']
            assert all(x['stat'][k] >= 0 for k in ('utime_ticks', 'stime_ticks', 'minflt', 'majflt'))
        chain = s['cgroup_ancestors']
        assert [g['path'] for g in chain] == [reg['expected_cgroup'], '/system.slice', '/']
        for g in chain:
            for name, item in g['files'].items():
                assert item['status'] in ('OK', 'UNAVAILABLE')
                if item['status'] == 'UNAVAILABLE': assert 'values' not in item and 'parsed' not in item
        table.append(dict(selector=key, pid=s['pid'], n_threads=len(s['threads']), tids=s['tids_before'],
            cgroup=s['cgroup_path'], ancestor_availability={g['path']:{name:x['status'] for name,x in g['files'].items()} for g in chain}))
    a, z = result['pool_before'], result['pool_after']
    assert a['tids_before'] == z['tids_before'] and a['start_ticks'] == z['start_ticks']
    for tid, old in a['threads'].items():
        new = z['threads'][tid]
        assert old['stat']['start_ticks'] == new['stat']['start_ticks']
        delta = {k:new['stat'][k]-old['stat'][k] for k in ('minflt','majflt','utime_ticks','stime_ticks')}
        delta.update({k:new['thread_status'][k]-old['thread_status'][k] for k in ('voluntary_ctxt_switches','nonvoluntary_ctxt_switches')})
        assert delta == result['pool_delta']['threads'][tid] and min(delta.values()) >= 0
    assert not result['nms_endpoint_recorded'] and not result['performance_endpoint_recorded']
    assert not result['simultaneous_execution_qualified'] and not result['observer_sham_qualified']
    output = dict(status='SAVED_SERVICE_POOL_METADATA_REPLAY_PASS', scientific_endpoint=False,
        raw_path='original/qa_result_01.json', raw_sha256=sha(B/'original/qa_result_01.json'),
        unit='native TID inventory, not image/latency/RSS', snapshot_table=table,
        all_native_thread_deltas_recomputed=True, original_file_count=2,
        original_bytes=sum(x['bytes'] for x in receipt['original_files'].values()),
        expected_thread_count_is_not_utilization=True, no_claim_about_nms_cause=True)
    with (B/'independent_saved_audit.json').open('x', encoding='utf-8') as f: json.dump(output, f, indent=2)
    print(json.dumps({k:v for k,v in output.items() if k != 'snapshot_table'}))


if __name__ == '__main__': main()
