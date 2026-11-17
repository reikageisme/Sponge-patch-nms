"""Replay saved native process/thread sampler data; no imports of runtime helper."""
from pathlib import Path
import hashlib
import json
import subprocess

B=Path(__file__).resolve().parent
ROOT=B.parents[2]
S=ROOT/'sponge-sim/studies/pi3b_nms_light_20261115'


def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    r=load(B/'original/qa_result_01.json');cfg=load(S/'qa_config.json');v=load(B/'verification.json')
    manifest=load(B/'original/qa_manifest.json');assert manifest==load(B/'qa_manifest.json')
    assert r['status']==v['status']=='PASS_LIGHT_RESOURCE_API_ONLY'
    assert r['commit']==manifest['commit'] and r['tag']==manifest['tag']==cfg['tag']
    assert r['config_sha256']==manifest['config_sha256']==sha(S/'qa_config.json')
    for name,digest in cfg['source_sha256'].items():
        assert sha(S/name)==digest
        blob=subprocess.check_output(['git','show',f"{r['commit']}:sponge-sim/studies/pi3b_nms_light_20261115/{name}"],cwd=ROOT)
        assert hashlib.sha256(blob).hexdigest()==digest
    first=json.loads(load(B/'terminal_before_fetch.json')['stdout'])
    last=json.loads(load(B/'terminal_after_fetch.json')['stdout'])
    assert first['files']==last['files']==v['original_files']
    for name,item in v['original_files'].items():
        assert sha(B/'original'/name)==item['sha256'] and (B/'original'/name).stat().st_size==item['bytes']
    assert first['source_sha256']==last['source_sha256']==cfg['source_sha256']
    invocation=load(B/'device_invocation.json')
    assert invocation['returncode']==0 and json.loads(invocation['stdout'])['unit_returncode']==0
    assert r['before_context']==r['after_context']
    a,z=r['before'],r['after'];assert a['pid']==z['pid']==a['calling_tid']==z['calling_tid']
    fields={'ru_minflt','ru_majflt','ru_nvcsw','ru_nivcsw'}
    for x in (a,z):
        for scope in ('process','calling_thread'):
            assert set(x[scope])==fields and all(type(q) is int and q>=0 for q in x[scope].values())
        assert 'ru_maxrss' not in x['process']
    clocks={k:z[k]-a[k] for k in ('process_cpu_ns','calling_thread_cpu_ns')}
    assert clocks==r['increments']['cpu_clocks'] and min(clocks.values())>=0
    for scope in ('process','calling_thread'):
        delta={k:z[scope][k]-a[scope][k] for k in fields}
        assert delta==r['increments'][scope] and min(delta.values())>=0
    for key in ('real_wall_bracket_exercised','observer_overhead_measured','model_or_nms_executed','rss_endpoint_recorded','scientific_timing_qualified'):
        assert r[key] is False
    result=dict(status='INDEPENDENT_LIGHT_RESOURCE_API_REPLAY_PASS',original_files=2,
        original_bytes=sum(x['bytes'] for x in v['original_files'].values()),raw_sha256=sha(B/'original/qa_result_01.json'),
        native_pid=r['before']['pid'],native_calling_tid=r['before']['calling_tid'],
        raw_selectors=['before.process','before.calling_thread','after.process','after.calling_thread','increments'],
        field_schema_replayed=True,all_native_deltas_recomputed=True,source_exact_tag=True,
        observer_overhead_or_operator_timing_inference=False)
    with (B/'independent_saved_audit.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(json.dumps(result))


if __name__=='__main__':main()
