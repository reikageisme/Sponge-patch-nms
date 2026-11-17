"""Functional-only configuration transition; no device/model/resource endpoint."""
from pathlib import Path
import hashlib
import json
import sys
from types import SimpleNamespace
import pytest

STUDY=Path(__file__).parents[1]/'studies/pi3b_renderer_prealloc_20261114'
sys.path.insert(0,str(STUDY))
import control


def lock():return json.loads((STUDY/'engineering_lock.json').read_text(encoding='utf-8'))


def test_functional_transition_keeps_every_tested_source_and_safety():
    new=lock();old=json.loads((STUDY.parents[1]/'results/pi3b_renderer_functional_cache_20261114/prior_engineering_lock.json').read_text(encoding='utf-8'))
    assert {k for k in old if old[k]!=new[k]}=={'qa_tag','allow_cache_preparation'}
    assert set(new)-set(old)=={'cache_plan_sha256'}
    assert new['allow_cache_preparation'] and not new['empirical_endpoints_enabled']
    assert not (STUDY/'memory_registration.json').exists()
    for name,digest in old['source_sha256'].items():assert hashlib.sha256((STUDY/name).read_bytes()).hexdigest()==digest


def test_new_context_passes_source_and_reference_binding(monkeypatch):
    monkeypatch.setattr(control,'ROOT',lock()['workspace'])
    assert control.locked_materials(STUDY)['allow_cache_preparation']


@pytest.mark.parametrize('change',[{'allow_cache_preparation':False},{'cache_plan_sha256':'0'*64}])
def test_unapproved_or_changed_functional_plan_cannot_apply_lease(tmp_path,monkeypatch,change):
    value=lock();value.update(change)
    monkeypatch.setenv('INVOCATION_ID','synthetic-plan-test')
    monkeypatch.setattr(control,'locked_materials',lambda *_:value)
    monkeypatch.setattr(control,'Lease',lambda *_:pytest.fail('no state changes for disabled/changed plan'))
    with pytest.raises(ValueError):control.payload(SimpleNamespace(mode='prepare',tag=value['qa_tag'],commit='a'*40,directory=tmp_path))


def test_scientific_mode_is_still_unregistered_before_any_lease(tmp_path,monkeypatch):
    value=lock()
    monkeypatch.setenv('INVOCATION_ID','synthetic-plan-test')
    monkeypatch.setattr(control,'locked_materials',lambda *_:value)
    monkeypatch.setattr(control,'Lease',lambda *_:pytest.fail('functional flag must not enable scientific endpoint'))
    with pytest.raises(FileNotFoundError):control.payload(SimpleNamespace(mode='memory',tag=value['qa_tag'],commit='a'*40,directory=tmp_path))
