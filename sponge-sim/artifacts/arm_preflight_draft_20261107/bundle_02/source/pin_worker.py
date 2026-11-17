"""Fresh-worker Torch pool diagnostics, not a standalone phone experiment.

execute_cell may ONLY be called by the future registered, sensor-supervised
launcher. No CLI is supplied. This module imports no Torch until after the
requested main-pin boundary. All four cells are diagnostics (two intra-op
threads on one requested CPU), not segmentation deployment profiles.
"""
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import sys
import time

from linux_observe import collect_threads,pin_all_current,pin_current
from pin_analysis import analyze


FIELDS={'cell_id','allowed_cpus','pool_order','pin_scope','torch_threads','matrix_size',
        'warmup_matmuls','intervals','interval_s','max_accounting_slack_fraction',
        'expected_torch_version','expected_torch_init_sha256'}


def validate(cfg):
    if set(cfg)!=FIELDS:raise ValueError('exact QA cell fields required')
    if not isinstance(cfg['cell_id'],str) or not cfg['cell_id']:
        raise ValueError('cell ID required')
    cpus=cfg['allowed_cpus']
    if not isinstance(cpus,list) or len(cpus)!=1 or type(cpus[0]) is not int or cpus[0]<0:
        raise ValueError('mechanism cells require one explicit logical CPU')
    if cfg['pool_order'] not in ('pin_before_pool','pool_before_pin') or cfg['pin_scope'] not in ('main','all'):
        raise ValueError('unknown pool order or pin scope')
    if type(cfg['torch_threads']) is not int or cfg['torch_threads']!=2:
        raise ValueError('diagnostic intra-op count fixed at two; not a deployment profile')
    for key,lo,hi in [('matrix_size',256,1024),('warmup_matmuls',1,100),('intervals',20,128)]:
        if type(cfg[key]) is not int or not lo<=cfg[key]<=hi:raise ValueError('invalid '+key)
    for key in ('interval_s','max_accounting_slack_fraction'):
        v=cfg[key]
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<v<=1:
            raise ValueError('invalid '+key)
    if cfg['intervals']*cfg['interval_s']>30:raise ValueError('nominal capture budget exceeds 30s')
    if not isinstance(cfg['expected_torch_version'],str) or not cfg['expected_torch_version'].strip():
        raise ValueError('runtime version must be locked from metadata')
    digest=cfg['expected_torch_init_sha256']
    if not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):
        raise ValueError('runtime init SHA must be locked from metadata')


def load_torch(cfg):
    torch=importlib.import_module('torch')
    digest=hashlib.sha256(Path(torch.__file__).read_bytes()).hexdigest()
    if str(torch.__version__)!=cfg['expected_torch_version'] or digest!=cfg['expected_torch_init_sha256']:
        raise RuntimeError('Torch version/init source changed since lock')
    return torch


def capture_window(work,cfg,observe,emit,*,wall_ns,cpu_ns,ticks_hz):
    """Sequential work/snapshots; both clocks bracket the whole observation.

    Snapshot collection + JSONL flush are INCLUDED in this QA window. No child,
    SSH or sensor-helper CPU time is added to this worker's process clock.
    Logs are flushed by the caller inside this owned worker; a blocked write
    is subject to parent safety/worker timeout, never parent-side unbounded IO.
    """
    c0=cpu_ns();t0=wall_ns();frames=[];counts=[]
    def sample(index):
        frame=observe(clock=lambda:wall_ns()/1e9)
        frames.append(frame);emit(dict(kind='thread_snapshot',index=index,frame=frame))
    sample(0)
    for index in range(cfg['intervals']):
        deadline=wall_ns()+int(cfg['interval_s']*1e9);count=0
        while not count or wall_ns()<deadline:
            work();count+=1
        counts.append(count);sample(index+1)
    t1=wall_ns();c1=cpu_ns()
    result=dict(window_start_ns=t0,window_end_ns=t1,process_cpu_start_ns=c0,process_cpu_end_ns=c1,
                window_start_s=t0/1e9,window_end_s=t1/1e9,process_cpu_s=(c1-c0)/1e9,
                ticks_hz=ticks_hz,matmul_counts=counts,frame_count=len(frames),
                snapshot_and_logging_overhead_included=True)
    emit(dict(kind='window_complete',**result))
    return frames,result


def execute_cell(cfg,emit):
    """One fresh isolated child only. emit must flush to its NEW raw JSONL.

    No retry on a partial pin or incomplete snapshot. Warmup/import are under
    parent thermal supervision too. A recorded diagnostic FAIL is preserved,
    not an exception used to search another CPU or repeat count.
    """
    validate(cfg)
    if 'torch' in sys.modules:raise RuntimeError('fresh process required: Torch already imported')
    if not hasattr(os,'sched_getaffinity'):raise RuntimeError('Linux affinity API required')
    emit(dict(kind='cell_started',config=cfg,scope='Torch mechanism control only, no segmentation/profile/DoS claim'))
    original=sorted(os.sched_getaffinity(0))
    if not set(cfg['allowed_cpus'])<=set(original):raise RuntimeError('requested CPU outside inherited allowed set')
    initial=collect_threads()
    emit(dict(kind='initial_threads',allowed=original,frame=initial,
              preloaded_modules={name:name in sys.modules for name in ('numpy','scipy','torch')}))
    if not initial['complete']:
        result=dict(status='preparation_failed',reason='initial_thread_snapshot_incomplete',profile_qualified=False)
        emit(dict(kind='cell_failed',result=result));return result
    for key in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'):os.environ[key]='2'
    if cfg['pool_order']=='pin_before_pool':pin_current(cfg['allowed_cpus'])
    torch=load_torch(cfg)
    torch.set_num_threads(2);torch.set_num_interop_threads(1)
    if torch.get_num_threads()!=2 or torch.get_num_interop_threads()!=1:
        raise RuntimeError('Torch threading readback mismatch')
    emit(dict(kind='runtime',version=str(torch.__version__),init_path=torch.__file__,
              init_sha256=cfg['expected_torch_init_sha256'],parallel_info=torch.__config__.parallel_info(),
              omp={k:os.environ[k] for k in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS')}))
    generator=torch.Generator(device='cpu');generator.manual_seed(20261107)
    n=cfg['matrix_size']
    a=torch.rand((n,n),dtype=torch.float32,device='cpu',generator=generator)
    b=torch.rand((n,n),dtype=torch.float32,device='cpu',generator=generator)
    out=torch.empty_like(a)
    with torch.inference_mode():
        work=lambda:torch.mm(a,b,out=out)
        for _ in range(cfg['warmup_matmuls']):work()
        emit(dict(kind='pool_warmed',frame=collect_threads()))
        if cfg['pool_order']=='pool_before_pin':pin_current(cfg['allowed_cpus'])
        if cfg['pin_scope']=='all':
            attempt=pin_all_current(cfg['allowed_cpus'])
            emit(dict(kind='all_tid_pin_attempt',attempt=attempt))
            if not attempt['readback_complete']:
                result=dict(status='preparation_failed',reason='all_tid_pin_incomplete',profile_qualified=False)
                emit(dict(kind='cell_failed',result=result));return result
        prepared=collect_threads()
        emit(dict(kind='prepared_threads',frame=prepared))
        if not prepared['complete']:
            result=dict(status='preparation_failed',reason='thread_snapshot_incomplete',profile_qualified=False)
            emit(dict(kind='cell_failed',result=result));return result
        hz=os.sysconf('SC_CLK_TCK')
        frames,window=capture_window(work,cfg,collect_threads,emit,wall_ns=time.perf_counter_ns,
                                     cpu_ns=time.process_time_ns,ticks_hz=hz)
        checksum=float(out.sum().item())
    qa=analyze(frames,cfg['allowed_cpus'],window['window_start_s'],window['window_end_s'],
               window['process_cpu_s'],window['ticks_hz'],
               max_accounting_slack_fraction=cfg['max_accounting_slack_fraction'])
    finite=math.isfinite(checksum)
    if not finite:
        qa.update(passed=False,decision='FAIL',reason='nonfinite_matrix_output')
    result=dict(status='diagnostic_recorded',qa=qa,checksum=checksum if finite else None,
                output_finite=finite,profile_qualified=False,
                scope='Two intra-op threads on one CPU; not a segmentation deployment profile')
    emit(dict(kind='cell_done',result=result))
    return result


def execute_to_raw(cfg,path):
    """Only the future supervised launcher may call this on a device.

    Flush each line inside this own worker so parent termination retains prior
    observations. A partial final line is kept as evidence, never overwritten.
    No claim of power-loss durability: unlike parent telemetry helpers, this
    raw worker sink does not fsync every observation inside the QA window.
    """
    with Path(path).open('x',encoding='utf-8',buffering=1) as raw:
        def emit(row):
            raw.write(json.dumps(dict(wall_utc=time.time(),**row),allow_nan=False)+'\n');raw.flush()
        try:return execute_cell(cfg,emit)
        except BaseException as e:
            emit(dict(kind='cell_exception',error=type(e).__name__,message=str(e)))
            raise


def child_exit_code(result):
    """A complete diagnostic FAIL is data; failed preparation is not completion.

    The parent supervisor resets the thermal-stop counter only for exit zero.
    Never let a preparation_failed return value become a safe completed burst.
    This status mapping supplies no scientific or deployment qualification.
    """
    if not isinstance(result,dict) or result.get('status')!='diagnostic_recorded':return 65
    qa=result.get('qa')
    if (result.get('profile_qualified') is not False or not isinstance(qa,dict)
            or qa.get('decision') not in ('PASS','FAIL','INCONCLUSIVE')
            or type(qa.get('passed')) is not bool
            or qa['passed']!=(qa['decision']=='PASS')):
        return 65
    finite=result.get('output_finite');checksum=result.get('checksum')
    if type(finite) is not bool:return 65
    if finite:
        if isinstance(checksum,bool) or not isinstance(checksum,(int,float)) or not math.isfinite(checksum):return 65
    elif checksum is not None or qa['decision']!='FAIL':return 65
    return 0


def execute_child(cfg,path):
    """Internal fresh-child callable for the future qualified device launcher.

    Caller must pass this integer to its process exit; do not discard it.
    Exceptions remain nonzero process failures with partial raw retained.
    No standalone load CLI is provided.
    """
    return child_exit_code(execute_to_raw(cfg,path))
