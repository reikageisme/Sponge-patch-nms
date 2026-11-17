"""Functional activation/forensics tests with synthetic tensors, no model/SSH."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import types

import pytest
import torch

B=Path(__file__).parents[1]/'results/pi3b_predecessor_material_qa_20261115'
modules={}
for name in ('device','audit_material'):
    spec=importlib.util.spec_from_file_location('prepared_material_'+name,B/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);modules[name]=module
d=modules['device'];audit=modules['audit_material']


@pytest.fixture
def synthetic_case():
    pred=torch.zeros(1,116,8400);pred[0,4,:2]=torch.tensor([.9,.8])
    boxes=torch.tensor([[1.,2.,3.,4.],[1.,2.,3.,4.]])
    storage=torch.zeros(43);scores=storage.as_strided((2,),(38,),4);scores.copy_(torch.tensor([.9,.8]))
    det=torch.zeros(1,38);det[0,:4]=boxes[0];det[0,4]=.9
    case=dict(protos=torch.zeros(32,160,160),coefficients=det[:,6:].clone().contiguous(),boxes=boxes[:1].clone(),shape=(640,640))
    frozen={key:value.clone() if torch.is_tensor(value) else value for key,value in case.items()}
    counts=dict(k=1,n_tau=2,kernel_n=2)
    def layout(t):return dict(shape=list(t.shape),stride=list(t.stride()),storage_offset=t.storage_offset(),dtype=str(t.dtype),device=str(t.device))
    kernel=dict(boxes=boxes,scores=scores,keep=torch.tensor([0]),detections=det,original_box_layout=layout(boxes),original_score_layout=layout(scores))
    def digest(t):return hashlib.sha256(memoryview(t.contiguous().numpy()).cast('B')).hexdigest()
    payload=dict(schema=1,image='000000000009',condition='adv',prediction=pred,mask_case=case,kernel=kernel,counts=counts)
    hashes=dict(prediction=digest(pred),**{k:digest(case[k]) for k in ('protos','coefficients','boxes')},kernel_boxes=digest(boxes),kernel_scores=digest(scores),keep=digest(kernel['keep']),detections=digest(det))
    frozen_row=dict(counts=counts,sha256='a'*64,mask_sha256='b'*64)
    row=dict(image='000000000009',condition='adv',counts=counts,content_sha256=hashes,kernel_box_layout=layout(boxes),kernel_score_layout=layout(scores),mask_sha256='b'*64,frozen_cache_sha256='a'*64,functional_only=True)
    return payload,row,frozen,frozen_row


def test_true_layout_counts_padding_frozen_parity_without_backend_rerun(synthetic_case):
    result=audit.inspect_case(*synthetic_case)
    assert result['true_kernel_n']==2 and result['retained_k']==1 and result['layout_preserved']
    assert not result['local_model_nms_or_mask_rerun']


@pytest.mark.parametrize('fault',['padding','layout','candidate_count','fresh_tensor','keep','hash','mask_digest'])
def test_corrupt_material_cannot_be_promoted(synthetic_case,fault):
    payload,row,frozen,frozen_row=synthetic_case
    if fault=='padding':payload['kernel']['scores'].as_strided((43,),(1,),0)[0]=123
    elif fault=='layout':payload['kernel']['scores']=payload['kernel']['scores'].contiguous()
    elif fault=='candidate_count':payload['prediction'][0,4,2]=.5
    elif fault=='fresh_tensor':payload['mask_case']['protos'][0,0,0]=1
    elif fault=='keep':payload['kernel']['keep']=torch.tensor([0,0])
    elif fault=='hash':row['content_sha256']['prediction']='f'*64
    elif fault=='mask_digest':row['mask_sha256']='f'*64
    with pytest.raises(ValueError):audit.inspect_case(payload,row,frozen,frozen_row)


def test_missing_tagged_admission_refuses_before_any_query(tmp_path,monkeypatch):
    monkeypatch.setattr(d,'B',tmp_path)
    monkeypatch.setattr(d.subprocess,'run',lambda *a,**k:pytest.fail('no SSH before admission'))
    with pytest.raises(FileNotFoundError):d.admission('a'*40)
    assert list(tmp_path.iterdir())==[]


def test_metadata_timeout_preserves_binary_prefix_and_never_retries(tmp_path,monkeypatch):
    monkeypatch.setattr(d,'B',tmp_path);calls=[]
    def fail(*args,**kwargs):calls.append(kwargs);raise subprocess.TimeoutExpired('fake SSH',300,output=b'partial\xff',stderr=b'error\r\n')
    monkeypatch.setattr(d.subprocess,'run',fail)
    with pytest.raises(subprocess.TimeoutExpired):d.query("print('null')",'query01')
    assert len(calls)==1 and (tmp_path/'requests/query01/stdout.bin').read_bytes()==b'partial\xff'
    assert json.loads((tmp_path/'requests/query01/receipt.json').read_text())['retry'] is False


def test_forensic_collection_keeps_failed_restore_source_data_not_false_pass(tmp_path,monkeypatch):
    monkeypatch.setattr(d,'B',tmp_path)
    data=b'original partial output';entry=dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
    response=dict(files={'partial.log':entry},original_restored=False,source_unchanged=False,prior_originals_unchanged=False)
    queries=[]
    def query(code,label):ast.parse(code);queries.append(label);return response
    monkeypatch.setattr(d,'query',query)
    def copy(*args,**kwargs):
        assert kwargs['timeout']==1800
        target=tmp_path/'runs/material_01/original';target.mkdir();(target/'partial.log').write_bytes(data)
        return types.SimpleNamespace(returncode=0,stdout='',stderr='')
    monkeypatch.setattr(d.subprocess,'run',copy)
    d.collect('a'*40,dict(package_sha256={},prior_originals={}))
    result=json.loads((tmp_path/'transfer_verification.json').read_text())
    assert result['remote_local_remote_sha_match'] and not result['independent_restore_verified']
    assert not result['source_and_prior_originals_unchanged'] and result['status']=='ORIGINALS_VERIFIED_NOT_A_FUNCTIONAL_VERDICT'
    assert queries==['collect_before','collect_after']


def test_missing_verified_deployment_prevents_model_frontend(tmp_path,monkeypatch):
    monkeypatch.setattr(d,'B',tmp_path)
    monkeypatch.setattr(d.subprocess,'Popen',lambda *a,**k:pytest.fail('no client without deployment'))
    with pytest.raises(FileNotFoundError):d.launch('a'*40,{})
