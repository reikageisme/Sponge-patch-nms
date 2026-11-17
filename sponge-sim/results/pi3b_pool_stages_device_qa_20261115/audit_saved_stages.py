"""Independent replay of saved stage identities/transitions, no observer import."""
from pathlib import Path
import hashlib
import json
import subprocess

B=Path(__file__).resolve().parent
ROOT=B.parents[2]
S=ROOT/'sponge-sim/studies/pi3b_pool_stages_20261115'


def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    r=load(B/'original/qa_result_01.json');cfg=load(S/'qa_config.json');v=load(B/'verification.json')
    manifest=load(B/'original/qa_manifest.json')
    assert manifest==load(B/'qa_manifest.json') and r['tag']==cfg['tag']==manifest['tag']
    assert r['commit']==manifest['commit'] and r['status']==v['status']=='PASS_STAGED_POOL_METADATA_ONLY'
    assert r['config_sha256']==manifest['config_sha256']==sha(S/'qa_config.json')
    for n,digest in cfg['source_sha256'].items():
        assert sha(S/n)==digest
        blob=subprocess.check_output(['git','show',f"{r['commit']}:sponge-sim/studies/pi3b_pool_stages_20261115/{n}"],cwd=ROOT)
        assert hashlib.sha256(blob).hexdigest()==digest
    a=json.loads(load(B/'terminal_before_fetch.json')['stdout']);b=json.loads(load(B/'terminal_after_fetch.json')['stdout'])
    assert a['files']==b['files']==v['original_files']
    assert a['source_sha256']==b['source_sha256']==cfg['source_sha256']
    for n,entry in v['original_files'].items():
        assert sha(B/'original'/n)==entry['sha256'] and (B/'original'/n).stat().st_size==entry['bytes']
    actual=load(B/'device_invocation.json')
    assert actual['returncode']==0 and json.loads(actual['stdout'])['unit_returncode']==0
    assert r['before_context']==r['after_context']
    assert r['python_version']==cfg['python_version'] and r['numpy_configuration']['version']==cfg['numpy_version']
    assert r['torch_configuration']['version']==cfg['torch_version'] and r['torch_configuration']['threads']==4
    for name in ('numpy_functional_check','torch_functional_check'):
        assert r[name]==dict(mm_invocations=1,shape=[512,512],exact_value=512,passed=True)
    stages=r['snapshots'];assert [s['label'] for s in stages]==cfg['stages']
    table=[];identities=[]
    for ix,s in enumerate(stages):
        x=s['inventory'];assert s['complete'] and x['complete_stable_set']
        assert x['cgroup_path']==cfg['expected_cgroup'] and x['tids_before']==x['tids_after']==sorted(int(t) for t in x['threads'])
        ids=set()
        for tid,t in x['threads'].items():
            assert t['status']=='OK' and t['affinity']==[0,1,2,3]
            birth=t['stat']['start_ticks'];ids.add((int(tid),birth))
            assert birth==x['end_start_ticks'][tid]['start_ticks']==s['thread_names'][tid]['start_ticks']
            assert s['thread_names'][tid]['status']=='OK'
        identities.append(ids)
        table.append(dict(label=s['label'],n_tids=len(ids),tids=sorted(int(t) for t in x['threads']),
            raw_selector=f'snapshots[{ix}].inventory.threads',library_selector=f'snapshots[{ix}].loaded_libraries'))
    replay=[]
    for ix,(old,new) in enumerate(zip(stages,stages[1:])):
        born=identities[ix+1]-identities[ix];gone=identities[ix]-identities[ix+1]
        result=dict(before=old['label'],after=new['label'],born_identities=[dict(tid=t,start_ticks=k) for t,k in sorted(born)],
            gone_identities=[dict(tid=t,start_ticks=k) for t,k in sorted(gone)],
            newly_mapped_libraries=sorted(set(new['loaded_libraries'])-set(old['loaded_libraries'])),
            temporal_cooccurrence_only=True,library_ownership_identified=False)
        assert result==r['transitions'][ix];replay.append(result)
    first,last=stages[-2]['inventory'],stages[-1]['inventory']
    assert identities[-2]==identities[-1]
    for tid,t in first['threads'].items():
        z=last['threads'][tid]
        values={k:z['stat'][k]-t['stat'][k] for k in ('minflt','majflt','utime_ticks','stime_ticks')}
        values.update({k:z['thread_status'][k]-t['thread_status'][k] for k in ('voluntary_ctxt_switches','nonvoluntary_ctxt_switches')})
        assert values==r['final_delta']['threads'][tid] and min(values.values())>=0
    kernel=r['kernel_metadata']
    assert kernel['proc']['cmdline']['status']=='OK'
    assert 'cgroup_disable=memory' in kernel['proc']['cmdline']['text'].split()
    # Missing memory proc row is absent, not enabled=False or a fabricated zero.
    assert 'memory' not in kernel['proc']['cgroups']['rows']
    assert not r['performance_endpoint_recorded'] and not r['nms_endpoint_recorded']
    output=dict(status='INDEPENDENT_STAGED_METADATA_REPLAY_PASS',raw_sha256=sha(B/'original/qa_result_01.json'),
        snapshots=len(stages),thread_observation_frames=sum(x['n_tids'] for x in table),stage_table=table,
        transitions=replay,raw_path='original/qa_result_01.json',scientific_endpoint=False,
        boot_cmdline_selector='kernel_metadata.proc.cmdline',kernel_flag_selector='kernel_metadata.kernel_config',
        original_files=2,original_bytes=sum(x['bytes'] for x in v['original_files'].values()),
        no_library_ownership_or_nms_causality_claim=True)
    with (B/'independent_saved_audit.json').open('x',encoding='utf-8') as f:json.dump(output,f,indent=2)
    print(json.dumps({k:v for k,v in output.items() if k not in ('stage_table','transitions')}))


if __name__=='__main__':main()
