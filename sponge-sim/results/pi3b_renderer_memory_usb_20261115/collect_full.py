# Adapted from sponge-sim/results/pi3b_renderer_memory_usb_20261115/collect_smoke.py:1-85
# SHA256 f338f5bf1747a493fcb0410af2f7bd5cbb73a5838ece9b028f51fa2ca02042e4; full-phase original collection and actual operational budget, no estimator change.
"""Fetch original terminal full files once, then audit; never launches a run."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
from deploy_science import B,SIM,SOURCE,REMOTE,OPTIONS,TAG,remote,save

PROBE=f'''from pathlib import Path
import sys,json,subprocess,hashlib
b=Path({REMOTE!r});sys.path.insert(0,str(b));import control
x=subprocess.run(['systemctl','show','sponge-pi3b-swapguard-v2.service','-p','ActiveState','-p','MainPID'],capture_output=True,text=True,timeout=10)
service=dict(line.split('=',1) for line in x.stdout.splitlines())
assert service.get('MainPID')=='0' and service.get('ActiveState') in ('inactive','failed'),service
r=b/'runs/memory_full_01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files={{p.relative_to(r).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(r.rglob('*')) if p.is_file()}}
restore=json.loads((r/'restore.json').read_text()) if (r/'restore.json').exists() else None
lease=json.loads((r/'lease_state.json').read_text()) if (r/'lease_state.json').exists() else None
snapshot=control.System().snapshot();masks=control.System().current()['masks']
norm=lambda rows:[{{k:v for k,v in row.items() if k!='used_kb'}} for row in rows]
matches=False
if lease and 'original' in lease:
 old=lease['original']
 matches=all(snapshot[k]==old[k] for k in ('governor','units','setup')) and norm(snapshot['swaps'])==norm(old['swaps']) and not any(masks.values())
workers=[]
roots=[b,b.with_name('pi3b_full20_20261114'),b.with_name('pi3b_renderer_prealloc_20261114')]
known={{str(root/n) for root in roots for n in ('control.py','run.py','memory_worker.py','memory_campaign.py','build_cache.py')}}
for p in Path('/proc').iterdir():
 if p.name.isdigit():
  try:
   argv=[v.decode(errors='replace') for v in (p/'cmdline').read_bytes().split(b'\\0') if v]
   if any(v in known for v in argv):workers.append(dict(pid=int(p.name),argv=argv))
  except OSError:pass
reg=json.loads((b/'memory_registration.json').read_text())
cache=Path(reg['cache_directory']);manifest=json.loads((cache/'manifest.json').read_text())
cached={{row['filename']:sha(cache/row['filename']) for row in manifest['cases']}}
print(json.dumps(dict(service=service,files=files,restore=restore,snapshot=snapshot,masks=masks,restore_readback_matches=matches,
 workers=workers,source_sha256={{n:sha(b/n) for n in reg['source_sha256']}},
 reference_sha256={{n:sha(b/n) for n in reg['reference_sha256']}},registration_sha256=sha(b/'memory_registration.json'),
 protocol_sha256=sha(b/reg['protocol']['filename']),cache_manifest_sha256=sha(cache/'manifest.json'),cached_tensor_sha256=cached,
 prelaunch_manifest_sha256=sha(b/'launch_manifests/full/manifest.json'),torch_imported='torch' in sys.modules)))
'''


def main():
    phase=B/'runs/memory_full_01';original=phase/'original'
    if not (phase/'manifest.json').exists():raise ValueError('No approved full launch manifest; do not fetch')
    if original.exists():raise FileExistsError('original destination exists; no overwrite/refetch')
    before=remote(PROBE);save('full_remote_before_fetch.json',dict(command=PROBE,result=before))
    r=subprocess.run(['scp',*OPTIONS,'-r',f'tanh@192.168.10.11:{REMOTE}/runs/memory_full_01',str(original)],capture_output=True,text=True,timeout=180)
    save('full_fetch_receipt.json',dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
    if r.returncode:raise RuntimeError('partial transfer retained; no overwrite retry')
    after=remote(PROBE);save('full_remote_after_fetch.json',dict(command=PROBE,result=after))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    files={p.relative_to(original).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in original.rglob('*') if p.is_file()}
    reg=json.loads((SOURCE/'memory_registration.json').read_text());manifest=json.loads((SOURCE/'cache_manifest.json').read_text())
    assert files==before['files']==after['files']
    for obs in (before,after):
        assert obs['source_sha256']==reg['source_sha256'] and obs['reference_sha256']==reg['reference_sha256']
        assert obs['registration_sha256']==sha(SOURCE/'memory_registration.json')
        assert obs['protocol_sha256']==reg['protocol']['sha256'] and obs['cache_manifest_sha256']==reg['cache_manifest_sha256']
        assert obs['cached_tensor_sha256']=={row['filename']:row['sha256'] for row in manifest['cases']}
        assert obs['prelaunch_manifest_sha256']==sha(phase/'manifest.json')
        assert not obs['workers'] and obs['torch_imported'] is False
    save('full_transfer_verification.json',dict(status='ALL_ORIGINAL_SMOKE_SHAS_REMOTE_LOCAL_REMOTE',original_files=len(files),files=files,
        runtime_source_unchanged=True,materials_unchanged=True,prelaunch_manifest_verified=True,
        restore_readback_verified=before['restore_readback_matches'] and after['restore_readback_matches'],ssh_kept_open=True))
    sys.path.insert(0,str(SOURCE));from analyze_memory import analyze
    summary=analyze(original,SOURCE/'memory_registration.json',SIM/'results/pi3b_renderer_functional_cache_20261114/caches/cache_01')
    with (phase/'summary.json').open('x',encoding='utf-8') as f:json.dump(summary,f,indent=2,allow_nan=False)
    rows=[json.loads(line) for line in (original/'memory/guards.jsonl').read_text().splitlines()] if (original/'memory/guards.jsonl').exists() else []
    elapsed=rows[-1]['wall_utc']-rows[0]['wall_utc'] if len(rows)>1 else None
    budget=dict(scope='Operational campaign duration/storage, not renderer latency',parent_guard_span_seconds=elapsed,
        fetched_original_bytes=sum(v['bytes'] for v in files.values()),raw_jobs=summary.get('audit',{}).get('n_jobs'),
        observed_full_guard_span_seconds=elapsed,
        estimate_is_not_guarantee=True,full_campaign_limit_seconds=21600,automatic_full_launch=False)
    save('full_operational_budget.json',budget)
    print(json.dumps(dict(status='FULL_COLLECTED_AND_AUDITED',original_files=len(files),
        quality_pass=summary['quality_pass'],
        audit=summary['audit'],budget=budget)))


if __name__=='__main__':main()
