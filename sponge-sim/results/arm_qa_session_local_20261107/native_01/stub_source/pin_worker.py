import json,math,sys
from pathlib import Path
FAIL_ID='1_pool_before_pin_main'
def execute_to_raw(cfg,path):
    assert 'torch' not in sys.modules
    if cfg['cell_id']==FAIL_ID:
        result=dict(status='preparation_failed',reason='engineering_fixture',profile_qualified=False)
        kind='cell_failed'
    else:
        result=dict(status='diagnostic_recorded',profile_qualified=False,output_finite=True,checksum=1.,
                    qa=dict(decision='FAIL',passed=False,reason='engineering_fixture'))
        kind='cell_done'
    with Path(path).open('x') as f:json.dump(dict(kind=kind,result=result,torch_imported=False,fixture=True),f)
    return result
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
