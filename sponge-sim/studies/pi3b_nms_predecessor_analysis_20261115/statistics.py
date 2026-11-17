"""Image-unit statistics for the draft; inputs must be finite complete cohorts.

MDE and percentile bootstrap follow the original frozen Pi statistics, with
provenance pinned in source_provenance.json. Sign-pattern chunking adapts the
independent RSS raw auditor (same two-sided rule/tolerance), not a fitted model.
"""
import math
from statistics import mean,stdev

import numpy as np
from scipy import stats as sps

SEED=2026111501
N_BOOT=20000


def moments(logs):
    if len(logs)<2 or not all(math.isfinite(x) for x in logs):raise ValueError('finite image-unit logs required')
    mu=mean(logs);sd=stdev(logs);n=len(logs)
    # Frozen central-t approximation, two-sided alpha.05, power.8, ddof1.
    mde=float((sps.t.ppf(.975,n-1)+sps.t.ppf(.8,n-1))*sd/math.sqrt(n))
    return dict(n_images=n,mean_log=mu,sd_log=sd,mde_log_80pct=mde,
        mde_method='central-t approximation; alpha=.05; power=.8; ddof=1',
        abs_mean_log_pass=abs(mu)<=.02,mde_log_pass=mde<=.05,
        numerical_gate_pass=abs(mu)<=.02 and mde<=.05,
        acceptance_is_not_formal_equivalence=True)


def exact_sign_flip(logs):
    if not 2<=len(logs)<=20 or not all(math.isfinite(x) for x in logs):raise ValueError('2..20 finite image logs required')
    x=np.asarray(logs,dtype=float);n=len(x);hits=0;obs=abs(mean(logs))
    for start in range(0,2**n,8192):
        patterns=np.arange(start,min(start+8192,2**n),dtype=np.uint32)
        signs=2*((patterns[:,None]>>np.arange(n,dtype=np.uint32))&1).astype(float)-1
        hits+=int((np.abs((signs*x).mean(axis=1))>=obs-1e-12).sum())
    return dict(p_sign_flip=hits/2**n,exact_sign_patterns=2**n,
        exact_extreme_patterns=hits,sign_flip_tolerance=1e-12)


def primary(logs):
    """Only a COMPLETE full20 numerical diagnostic; no quality authorization."""
    if len(logs)!=20:raise ValueError('full20 inference requires all20 image units')
    out=moments(logs);x=np.asarray(logs,dtype=float)
    draws=np.random.default_rng(SEED).integers(0,len(x),(N_BOOT,len(x)))
    lo,hi=np.quantile(x[draws].mean(axis=1),[.025,.975])
    out.update(geomean_ratio=math.exp(out['mean_log']),ratio_ci95=[math.exp(float(lo)),math.exp(float(hi))],
        dz=None if out['sd_log']==0 else out['mean_log']/out['sd_log'],
        zero_sd_means_no_standardized_effect_estimate=out['sd_log']==0,
        bootstrap_seed=SEED,n_boot=N_BOOT,unit='image; reused cohort; one attack initialization',
        confirmatory_interpretation_authorized=False,**exact_sign_flip(logs))
    # Primary is an effect estimate, not itself an A/A acceptance test.
    for key in ('abs_mean_log_pass','mde_log_pass','numerical_gate_pass','acceptance_is_not_formal_equivalence'):out.pop(key)
    return out
