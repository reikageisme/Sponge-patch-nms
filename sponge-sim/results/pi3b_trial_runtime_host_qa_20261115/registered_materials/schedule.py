# Copied unchanged from sponge-sim/studies/pi3b_nms_predecessor_20261115/schedule.py:1-27
# SHA256 acfe063a7f0f9bc8dbdaa650a2629003d09e0ee91c3f89a381640a4205245d25; original runtime/tag immutable.
"""Fixed draft factorial schedule. No launch/benchmark or empirical data."""
import random

IMAGE_IDS=tuple(f'{x:012d}' for x in (9,25,30,34,36,42,49,61,64,71,72,73,74,77,78,81,86,89,92,94))
PREDECESSORS=('native32M','candidate16M','nms_reference')
TARGETS=('wrapper','kernel_call','sham')
OBSERVERS=('uninstrumented','instrumented')
COPIES=('A','B')
REPEATS=5
SEED=20261115


def schedule(image_ids):
    ids=list(image_ids)
    if not ids or len(set(ids))!=len(ids) or any(x not in IMAGE_IDS for x in ids):
        raise ValueError('unique frozen image subset required')
    if ids!=sorted(ids,key=IMAGE_IDS.index):raise ValueError('frozen master order required')
    rows=[]
    for image in ids:
        ix=IMAGE_IDS.index(image)
        for rep in range(REPEATS):
            cells=[(p,t,o,c) for p in PREDECESSORS for t in TARGETS for o in OBSERVERS for c in COPIES]
            random.Random(SEED+1000*ix+rep).shuffle(cells)
            for position,(p,t,o,c) in enumerate(cells):
                rows.append(dict(index=len(rows),image=image,master_index=ix,rep=rep,position=position,
                    predecessor=p,target=t,observer=o,copy=c))
    return rows
