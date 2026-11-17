"""Supervised four-cell QA composition, not an approved device entry point.

The future registered device launcher supplies a fresh-child spawn(cfg),
durable/deadline-bounded telemetry and events, and current state/qualification
bindings. spawn MUST return its newly owned child immediately, launch a fresh
interpreter, retain raw/partials, and use pin_worker.execute_child's exit code.
No device access, Torch import, auto-discovery or standalone load CLI here.
"""
import hashlib
import json
import os
from pathlib import Path
import random
import sys

from pin_worker import validate
from posix_runtime import OwnGroup,stop_group,write_new_json
from session import run_session

SOURCE_FILES=('checks.py','linux_observe.py','posix_runtime.py','session.py',
              'pin_analysis.py','pin_worker.py','qa_session.py')

# Internal fresh-child entry only. Parent PID is a startup consistency check,
# NOT a parent-death guarantee; Android/proot death/descendant QA is still open.
CHILD_CODE='''import hashlib,json,os,sys
from pathlib import Path
source=Path(sys.argv[1]);expected=json.loads(sys.argv[5])
if os.getppid()!=int(sys.argv[6]):raise RuntimeError('supervisor changed before worker start')
for name,digest in expected.items():
    if hashlib.sha256((source/name).read_bytes()).hexdigest()!=digest:raise RuntimeError('worker source changed')
data=Path(sys.argv[2]).read_bytes()
if hashlib.sha256(data).hexdigest()!=sys.argv[3]:raise RuntimeError('cell configuration changed')
sys.path.insert(0,str(source))
from pin_worker import execute_child
raise SystemExit(execute_child(json.loads(data),sys.argv[4]))
'''


def validate_cells(cells):
    """Lock the whole plan before any gate/spawn; no outcome-selected cells."""
    cells=json.loads(json.dumps(cells,allow_nan=False))
    if not isinstance(cells,list) or len(cells)!=4:
        raise ValueError('exact four-cell fixed plan required')
    order=[(p,s) for p in ('pin_before_pool','pool_before_pin') for s in ('main','all')]
    random.Random(20261107).shuffle(order)
    ids=[];common=None
    for index,(cfg,pair) in enumerate(zip(cells,order),1):
        validate(cfg)
        expected_id=f'{index}_{pair[0]}_{pair[1]}'
        if (cfg['pool_order'],cfg['pin_scope'])!=pair or cfg['cell_id']!=expected_id:
            raise ValueError('prospective fixed cell order/identity changed')
        shared={k:v for k,v in cfg.items() if k not in ('cell_id','pool_order','pin_scope')}
        if common is None:common=shared
        if shared!=common:raise ValueError('CPU/runtime/workload settings must match across cells')
        ids.append(cfg['cell_id'])
    if len(set(ids))!=4:raise ValueError('unique cell IDs required')
    return cells


class CellSpawner:
    """Prepare exclusive workspace files, then spawn only the four locked cells.

    Use as a context manager around run_cells. Source/config checks precede
    every child, which repeats them before Torch import. No tag, device-QA or
    operator-state approval is manufactured here. The external device entry
    remains forbidden until those actual bindings and physical QA exist.
    """
    def __init__(self,cells,workspace,directory,source,source_sha256):
        cells=validate_cells(cells)
        self.workspace=Path(workspace).resolve(strict=True)
        self.directory=Path(directory).resolve();self.source=Path(source).resolve(strict=True)
        if (self.directory==self.workspace or not self.directory.is_relative_to(self.workspace)
                or not self.source.is_relative_to(self.workspace)):
            raise ValueError('source and NEW run directory must stay inside workspace')
        if set(source_sha256)!=set(SOURCE_FILES):raise ValueError('exact executed source bindings required')
        self.hashes=dict(source_sha256);self.rows={};self.cleanup_errors=[]
        self.verify_source()
        self.directory.mkdir(parents=True,exist_ok=False)
        try:
            for cfg in cells:
                name=cfg['cell_id'];config=self.directory/(name+'.json')
                digest=write_new_json(config,cfg)
                self.rows[name]=dict(config=config,sha256=digest,raw=self.directory/(name+'.jsonl'),
                                     log=(self.directory/(name+'.log')).open('xb',buffering=0),started=False,child=None)
            write_new_json(self.directory/'plan.json',dict(cells=cells,source_sha256=self.hashes,
                                                         status='PREPARED_NOT_DEVICE_QUALIFICATION'))
        except BaseException:
            for row in self.rows.values():row['log'].close()
            raise

    def verify_source(self):
        for name,digest in self.hashes.items():
            if hashlib.sha256((self.source/name).read_bytes()).hexdigest()!=digest:
                raise ValueError('source changed since binding: '+name)

    def spawn(self,cfg):
        name=cfg['cell_id'];row=self.rows[name]
        if row['started']:raise RuntimeError('cell already attempted; no retry')
        row['started']=True
        self.verify_source()
        data=row['config'].read_bytes()
        if hashlib.sha256(data).hexdigest()!=row['sha256'] or json.loads(data)!=cfg:
            raise ValueError('locked cell configuration changed')
        args=[sys.executable,'-c',CHILD_CODE,str(self.source),str(row['config']),row['sha256'],
              str(row['raw']),json.dumps(self.hashes,sort_keys=True),str(os.getpid())]
        child=OwnGroup(args,self.workspace,stdout=row['log'])
        row['child']=child  # no logging or file operations after process creation
        return child

    def close(self):
        errors=[];fatal=None
        try:
            for name,row in self.rows.items():
                if row['child'] is None:continue
                try:stop_group(row['child'])
                except BaseException as e:
                    errors.append(dict(cell_id=name,error=type(e).__name__,message=str(e)))
                    if not isinstance(e,Exception) and fatal is None:fatal=e
        finally:
            for row in self.rows.values():row['log'].close()
        self.cleanup_errors=errors
        if fatal is not None:raise fatal
        if errors:raise RuntimeError('owned QA child cleanup unresolved: '+json.dumps(errors))

    def __enter__(self):return self

    def __exit__(self,*exc):self.close()


def run_cells(cells,guard,spawn,read,emit,clock,wait,config):
    """Execute each planned cell at most once, under the existing guard.

    Control completion is never profile qualification. Existing run_session
    retains interrupted/not-started bursts and mandatory rest/cooldown. This
    outer owner also finalizes every captured child and requires a separate
    post-cleanup journal ACK, since coordinator terminal ACK precedes this
    final ownership check. No retry or reordering after diagnostic failure.
    """
    cells=validate_cells(cells)
    plan_sha=hashlib.sha256(json.dumps(cells,sort_keys=True,allow_nan=False).encode()).hexdigest()
    owned=[None]*4
    plan=[]
    for index,cfg in enumerate(cells):
        def factory(i=index,c=cfg):
            child=spawn(c)
            owned[i]=child  # retain ownership before returning to supervisor
            return child
        plan.append((cfg['cell_id'],factory))
    def sink(event):
        if event['kind']=='session_started':
            event=dict(event,qa_plan_sha256=plan_sha,worker_exit_contract='pin_worker.execute_child',
                       profile_qualified=False)
        return emit(event)
    result=None;fatal=None
    try:
        result=run_session(guard,plan,read,sink,clock,wait,config)
    except BaseException as e:
        fatal=e
        guard.state='END'
        result=dict(status='qa_runner_exception',study_quality='NOT_ASSESSED',
                    error=type(e).__name__,message=str(e),terminal_journal_ack=False,
                    cells_started=[cells[i]['cell_id'] for i,c in enumerate(owned) if c is not None])
    cleanup_errors=[]
    for i,child in enumerate(owned):
        if child is None:continue
        try:stop_group(child)
        except BaseException as e:
            cleanup_errors.append(dict(cell_id=cells[i]['cell_id'],pgid=getattr(child,'pgid',None),
                                       error=type(e).__name__,message=str(e)))
            if not isinstance(e,Exception) and fatal is None:fatal=e
    if cleanup_errors:
        guard.state='END';result.update(status='qa_cleanup_error',cleanup_errors=cleanup_errors)
    result.update(guard_state=guard.state,qa_plan_sha256=plan_sha,profile_qualified=False,
                  qa_terminal_journal_ack=False)
    try:
        emit(dict(kind='qa_terminal',result={k:v for k,v in result.items() if k!='qa_terminal_journal_ack'}))
        result['qa_terminal_journal_ack']=True
    except BaseException as e:
        guard.state='END'
        result.update(status='qa_journal_error',guard_state='END',qa_journal_error=type(e).__name__,
                      qa_journal_message=str(e))
        if not isinstance(e,Exception) and fatal is None:fatal=e
    if fatal is not None:raise fatal
    return result
