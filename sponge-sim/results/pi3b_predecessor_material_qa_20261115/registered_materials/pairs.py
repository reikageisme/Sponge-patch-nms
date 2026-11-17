"""Prepared immediate predecessor-target execution; not a scientific launcher.

Caller prepares clones/closures and completes guards/intent BEFORE execute.
Return live target output; caller releases it before post-guard/logging.
There is no callback for hidden intervening work or for a different clock.
"""
import gc
import bracket


def execute(predecessor,target,*,instrumented):
    if type(instrumented) is not bool:raise TypeError('explicit boolean observer mode required')
    bracket.require_setup()
    enabled=gc.isenabled();gc.disable()
    try:
        previous=predecessor()
        del previous
        if gc.isenabled():raise RuntimeError('predecessor changed GC state')
        return bracket.measure(target,instrumented=instrumented)
    finally:
        if enabled:gc.enable()
        else:gc.disable()
