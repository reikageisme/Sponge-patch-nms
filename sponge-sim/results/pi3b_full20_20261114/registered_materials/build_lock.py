# Copied from sponge-sim/studies/pi3b_600mhz_swapguard_v2/build_lock.py:1-43
# SHA256 58cddc2682861109884a222534c123d9ce12e6144a1e5e80cf3832c86d589e2d; parent protocol remains CLOSED and immutable.
"""Build a NEW lock from unchanged Pi input bytes; never rewrite the old lock.

Source: studies/pi3b_600mhz/build_lock.py:1-66,
SHA256 dda544961de8c24d6b49441800cab428dfd7d8ff27a061051bc8af252f792429.
"""
from pathlib import Path
import hashlib
import json
from scipy import stats as sps
from control import record

HERE=Path(__file__).resolve().parent
SIM=HERE.parents[1]


def main():
    old=SIM/'studies'/'pi3b_600mhz'/'lock.json'
    lock=json.loads(old.read_text(encoding='utf-8'))
    material=SIM/'results'/'laptop_seg_20261107'
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    rows=[dict(r) for r in lock['files'] if r['name'] in lock['inputs']+[lock['weights']]]
    assert len(rows)==21
    for row in rows:
        assert sha(material/row['name'])==row['sha256'],row['name']
    names=['run.py','guard.py','audit.py','analyze.py','control.py','stats_frozen.py','build_lock.py']
    rows += [dict(name=n,sha256=sha(HERE/n),bytes=(HERE/n).stat().st_size) for n in names]
    lock.update(experiment='PI3B-FULL20-POST-PILOT',files=rows,
                registration_tag='prereg-pi3b-full20-after-pilot-20261114',
                qa_tag='qa-pi3b-full20-20261114',
                mde_t_critical_sums={str(n):float(sps.t.ppf(.975,n-1)+sps.t.ppf(.8,n-1)) for n in (2,20)},
                reference_counts_sha256=sha(SIM/'results'/'pi3b_600mhz_20261114'/'laptop_reference_counts.json'),
                previous_lock_sha256=sha(old),
                guard_policy='pre_post_every_clocked_call_v2',
                parent_protocol_lock_sha256='2041162d361e37a8a2bf045d1f58d05d181a0f16b1e13d552d7b8eb74ea00d23',
                pilot_policy='retain_failed_v2_pilot_no_repeat_smoke',
                stage_aa=dict(arms=['nms_adv_B','mask_adv_B'],full_required=True,smoke_descriptive_only=True),
                campaign=dict(settle_seconds=dict(smoke=10,full=60),
                              session_order=[['PI4','pipeline'],['PI4','stages'],['PI1','pipeline']],
                              session_timeout_seconds=14400,total_timeout_seconds=21600))
    # Operational preparation step, not a result file. Do not invoke after the new tag.
    record(HERE/'lock.json',lock)
    print('new lock SHA256',sha(HERE/'lock.json'))


if __name__=='__main__':
    main()
