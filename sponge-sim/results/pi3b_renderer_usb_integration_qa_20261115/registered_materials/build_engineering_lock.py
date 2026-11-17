# Copied/adapted from sponge-sim/studies/pi3b_renderer_memory_v1_20261114/build_engineering_lock.py:1-28
# SHA256 ee5093542ee70312d8c06b80a49add0a47d1fb5622a76ffa15245f33753ad293; closed USB-absent V1 source/runs remain immutable.
"""Freeze sleeping-only QA in the new RSS namespace; never enables RSS by itself."""
from pathlib import Path
import hashlib
import json
from memory_worker import SOURCE_FILES
HERE=Path(__file__).resolve().parent
SIM=HERE.parents[1]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def build():
    cache=SIM/'results/pi3b_renderer_functional_cache_20261114'
    manifest=cache/'caches/cache_01/manifest.json';audit=cache/'functional_audit.json'
    if sha(manifest)!='61b5abaaf22ea985b98f582a34f52cc19c2272ac87f66782292d843b17bbe165':raise ValueError('immutable cache cohort differs')
    for name,p in (('cache_manifest.json',manifest),('cache_functional_audit.json',audit)):
        with (HERE/name).open('xb') as f:f.write(p.read_bytes())
    old=json.loads((HERE.parent/'pi3b_full20_20261114/lock.json').read_text(encoding='utf-8'))
    value=dict(workspace='/home/tanh/sponge-sim/pi3b_renderer_memory_usb_20261115',qa_tag='qa-pi3b-renderer-memory-usb-20261115',
        empirical_endpoints_enabled=False,source_sha256={n:sha(HERE/n) for n in sorted(SOURCE_FILES|{'build_engineering_lock.py'})},
        reference_sha256={n:sha(HERE/n) for n in ('cache_manifest.json','cache_functional_audit.json','usb_contract.json')},
        safety={k:old[k] for k in ('governor','gates')})
    with (HERE/'engineering_lock.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2)
    print('Created sleeping-QA source lock. No scientific registration created.')


if __name__=='__main__':build()
