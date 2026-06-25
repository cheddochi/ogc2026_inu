"""HH active submission wrapper.

Current active working line:
    reboot_v194_20260626_familyA_fourbay_inline_on_v186

Publish-trust note:
    v194 is the current-tree trusted BEST. It keeps the prob_20 / prob_38 /
    prob_39 / prob_40 guard surface from the trusted v186 line while adding a
    narrow 4-bay Family A inline postpass that lowers Total T and objective on
    the train40 benchmark.
"""

from alg_versions import reboot_v194_20260626_familyA_fourbay_inline_on_v186 as active


ACTIVE_VERSION = "reboot_v194_20260626_familyA_fourbay_inline_on_v186"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
