"""Strict engineering package/USB/functional activation bindings; no Torch."""
from pathlib import Path
import hashlib
import json
import re

HERE=Path(__file__).resolve().parent
ROOT=Path('/home/tanh/sponge-sim/pi3b_nms_predecessor_20261115')
SERVICE='sponge-pi3b-swapguard-v2.service'
SOURCE_FILES=set('baseline_ops.py bracket.py cache.py factories.py kernel_input.py material.py pairs.py preallocate.py schedule.py guard.py usb_guard.py control.py bindings.py campaign.py worker.py exports.py inventory.py counters.py build_controller_lock.py'.split())
REFERENCES={'full20_lock.json','cache_manifest.json','usb_contract.json'}
FULL_LOCK_SHA='1cd1789d4f30c0a6b708fad907729999f6e6e53d4ba373ce487bc8037d10be0e'
CACHE_MANIFEST_SHA='61b5abaaf22ea985b98f582a34f52cc19c2272ac87f66782292d843b17bbe165'


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for x in iter(lambda:f.read(1024*1024),b''):h.update(x)
    return h.hexdigest()


def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def read_lock(base=HERE):
    base=Path(base).resolve();lock=load(base/'controller_lock.json')
    if lock['workspace']!=str(ROOT) or base!=ROOT.resolve() or lock['empirical_endpoints_enabled'] is not False:
        raise ValueError('wrong supervised engineering workspace')
    if set(lock['source_sha256'])!=SOURCE_FILES or set(lock['reference_sha256'])!=REFERENCES:
        raise ValueError('incomplete package source/reference binding')
    for name,digest in {**lock['source_sha256'],**lock['reference_sha256']}.items():
        if sha(base/name)!=digest:raise ValueError('registered bytes changed: '+name)
    if sha(base/'full20_lock.json')!=FULL_LOCK_SHA or sha(base/'cache_manifest.json')!=CACHE_MANIFEST_SHA:
        raise ValueError('original material identities differ')
    if lock['functional_enabled'] is not False or lock['scientific_enabled'] is not False:
        raise ValueError('base lock cannot enable a model or timing')
    return lock


def load_usb_preflight(path,tag,commit,phase,lock_sha256,contract):
    # Adapted from sponge-sim/studies/pi3b_renderer_memory_usb_20261115/memory_worker.py:83-93,
    # SHA256 51d65dfd10f7a3854192206da0b240eb55912d70aa36628ef4b90f3c20d6dcda;
    # new engineering phases only, original scientific registrations untouched.
    import usb_guard
    raw=Path(path).read_bytes();info=json.loads(raw)
    if info!=dict(tag=tag,commit=commit,phase=phase,lock_sha256=lock_sha256,
        usb_contract_sha256=sha(HERE/'usb_contract.json'),snapshot=info.get('snapshot')):
        raise ValueError('USB phase binding differs')
    if phase not in ('qa','functional') or usb_guard.validate(info['snapshot'],contract):
        raise ValueError('invalid/non-idle original phase frame')
    return info['snapshot'],hashlib.sha256(raw).hexdigest()


def activation(base=HERE):
    base=Path(base);value=load(base/'functional_activation.json');lock=read_lock(base)
    if (value['functional_only_enabled'] is not True or value['scientific_enabled'] is not False
        or value['tag']!='qa-pi3b-nms-predecessor-material-20261115'
        or value['controller_lock_sha256']!=sha(base/'controller_lock.json')
        or value['supervisor_qa_sha256']!=sha(base/'supervisor_qa_verification.json')
        or value['cases']!=40 or value['campaign_timeout_seconds']!=3600):
        raise ValueError('functional activation differs')
    review=load(base/'supervisor_qa_verification.json')
    if (review['status']!='ALL_FIVE_SLEEP_CASES_PASS' or review['source_sha256']!=lock['source_sha256']
        or review['controller_lock_sha256']!=sha(base/'controller_lock.json')):
        raise ValueError('supervisor qualification missing/different')
    return value


def valid_identity(tag,commit):
    if not re.fullmatch('[a-z0-9-]+',tag or '') or not re.fullmatch('[0-9a-f]{40}',commit or ''):
        raise ValueError('invalid tag/commit')
