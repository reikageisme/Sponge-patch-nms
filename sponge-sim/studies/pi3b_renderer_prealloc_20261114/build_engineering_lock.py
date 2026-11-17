"""Create ONLY a source-bound sleeping-QA lock; never a scientific registration."""
from pathlib import Path
import hashlib
import json
from memory_worker import SOURCE_FILES

HERE=Path(__file__).resolve().parent
SIM=HERE.parents[1]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    old=HERE.parent/'pi3b_full20_20261114/lock.json'
    summary=SIM/'results/pi3b_full20_20261114/runs/full_01/summary.json'
    if sha(old)!='1cd1789d4f30c0a6b708fad907729999f6e6e53d4ba373ce487bc8037d10be0e':raise ValueError('parent lock changed')
    if sha(summary)!='34166aa9972cd0ffac8af3524a15565eb2ea94235c3f640de9312603e6799ca3':raise ValueError('reference changed')
    for name,source in (('full20_lock.json',old),('full20_summary.json',summary)):
        with (HERE/name).open('xb') as f:f.write(source.read_bytes())
    oldlock=json.loads(old.read_text(encoding='utf-8'))
    value=dict(workspace='/home/tanh/sponge-sim/pi3b_renderer_prealloc_20261114',qa_tag='qa-pi3b-renderer-memory-20261114',
               empirical_endpoints_enabled=False,allow_cache_preparation=False,
               source_sha256={name:sha(HERE/name) for name in sorted(SOURCE_FILES|{'build_engineering_lock.py'})},
               safety={k:oldlock[k] for k in ('governor','gates')},
               reference_sha256={name:sha(HERE/name) for name in ('full20_lock.json','full20_summary.json')})
    with (HERE/'engineering_lock.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2)
    return value


if __name__=='__main__':
    result=build();print('Created engineering-only lock for',len(result['source_sha256']),'source files; cache and empirical endpoints disabled.')
