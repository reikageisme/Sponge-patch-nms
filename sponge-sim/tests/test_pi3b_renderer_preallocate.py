"""Finite functional parity and source provenance only; no benchmark clocks."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import pytest
import torch

STUDY=Path(__file__).parents[1]/'studies/pi3b_renderer_prealloc_20261114'
sys.path.insert(0,str(STUDY))
from preallocate import process_mask_preallocated
from baseline_ops import process_mask_native


@pytest.mark.parametrize('shape,proto,k',[
    ((20,24),(4,5,6),0),((20,24),(4,5,6),1),((20,24),(4,5,6),7),
    ((31,47),(4,7,9),40),((7,9),(4,7,9),40),((640,640),(32,160,160),300),
    ((640,640),(4,8,8),39),((640,640),(4,8,8),40),
    ((640,640),(4,8,8),78),((640,640),(4,8,8),79),
])
def test_exact_parity_including_chunk_boundaries_and_boxes(shape,proto,k):
    g=torch.Generator().manual_seed(20261114+k)
    protos=torch.randn(proto,generator=g)
    coeff=torch.randn((k,proto[0]),generator=g)
    boxes=torch.randn((k,4),generator=g)*max(shape)
    if k:
        boxes[:,2:]=boxes[:,:2]+boxes[:,2:].abs()
        boxes[0]=torch.tensor([-5.,-4.,shape[1]+2.,shape[0]+2.])
        if k>1:boxes[1]=0  # empty crop
    initial=[x.clone() for x in (protos,coeff,boxes)]
    with torch.inference_mode():
        expected=process_mask_native(protos,coeff,boxes,shape)
        for budget in (32_000_000,16_000_000,2*shape[0]*shape[1]):
            got=process_mask_preallocated(protos,coeff,boxes,shape,pixel_budget=budget)
            assert got.dtype==torch.uint8 and got.shape==(k,*shape)
            assert torch.equal(got,expected)
    assert all(torch.equal(a,b) for a,b in zip(initial,(protos,coeff,boxes)))


def test_zero_logits_threshold_and_noncontiguous_coefficients():
    p=torch.zeros((4,5,6));c=torch.ones((7,8))[:,::2];b=torch.tensor([[0.,0.,24.,20.]]*7)
    with torch.inference_mode():
        ref=process_mask_native(p,c,b,(20,24));got=process_mask_preallocated(p,c,b,(20,24),pixel_budget=960)
    assert torch.equal(ref,got) and not got.any()


def test_frozen_helpers_match_actual_locked_package_source():
    spec=importlib.util.find_spec('ultralytics');p=Path(spec.origin).parent/'utils/ops.py'
    provenance=json.loads((STUDY/'provenance.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(p.read_bytes()).hexdigest()==provenance['source_sha256']
    src=ast.parse(p.read_text(encoding='utf-8'));copied=ast.parse((STUDY/'baseline_ops.py').read_text())
    for name in ('crop_mask','scale_masks','process_mask_native'):
        original=next(n for n in src.body if isinstance(n,ast.FunctionDef) and n.name==name)
        reference=next(n for n in copied.body if isinstance(n,ast.FunctionDef) and n.name==name)
        assert ast.dump(original)==ast.dump(reference)
