"""Prepared readiness-query evidence capture; no automatic retry or launcher.

Original remote() contract: results/pi3b_predecessor_supervisor_qa_20261115/
run_device_qa.py:36-40, SHA256
87198d9ace7e7e071e0ede70caa9b1342183f646d3c740ed1acd3e50a82ac0e6.
Retains request cap25s; caller remaining budget can only shorten it. No native
query is authorized by this module. Tests replace subprocess.run entirely.
"""
import ast
import json
import math
from pathlib import Path
import subprocess

SSH=['ssh','-i',str(Path.home()/'.ssh/pi_spongepi'),'-oBatchMode=yes',
    '-oStrictHostKeyChecking=yes','-oConnectTimeout=10','tanh@192.168.10.11',
    '/home/tanh/sponge-venv/bin/python -']


def capture(code,remaining,directory):
    """One query, byte-exact streams including timeout prefixes, exclusive paths."""
    if type(remaining) not in (int,float) or not math.isfinite(remaining) or remaining<=0:
        raise ValueError('positive finite remaining readiness budget required')
    ast.parse(code)
    directory=Path(directory);directory.mkdir(exist_ok=False)
    (directory/'stdin.py').write_bytes(code.encode('utf-8'))
    timeout=min(25,remaining);status='LAUNCH_ERROR';stdout=b'';stderr=b'';returncode=None;error=None;value=None
    try:
        result=subprocess.run(SSH,input=code.encode('utf-8'),capture_output=True,timeout=timeout)
        stdout=result.stdout;stderr=result.stderr;returncode=result.returncode
        if returncode:raise RuntimeError('readiness query exit code '+str(returncode))
        # JSON constants NaN/Infinity are not evidence of a valid READY result.
        def invalid_constant(x):raise ValueError('non-finite JSON constant: '+x)
        value=json.loads(stdout,parse_constant=invalid_constant);status='JSON_RESPONSE_RECEIVED'
    except subprocess.TimeoutExpired as exc:
        stdout=exc.stdout or b'';stderr=exc.stderr or b'';status='TIMEOUT_NO_RETRY'
        error=dict(type=type(exc).__name__,message='readiness query exceeded its fixed remaining budget')
        raise
    except BaseException as exc:
        status='QUERY_OR_PARSE_ERROR' if returncode is not None else 'LAUNCH_ERROR'
        error=dict(type=type(exc).__name__,message=str(exc));raise
    finally:
        for name,data in (('stdout.bin',stdout),('stderr.bin',stderr)):
            with (directory/name).open('xb') as f:f.write(data)
        with (directory/'receipt.json').open('x',encoding='utf-8') as f:
            json.dump(dict(status=status,returncode=returncode,error=error,timeout_seconds=timeout,
                automatic_retry=False,response_received=status=='JSON_RESPONSE_RECEIVED',
                response_is_not_itself_a_qualified_readiness_observation=True),f,indent=2)
    return value
