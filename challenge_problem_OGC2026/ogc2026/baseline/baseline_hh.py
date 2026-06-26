"""HH active submission wrapper.

Current active working line:
    reboot_v218_20260627_trackA_dense_fourbay_deep_chain_on_v217

Publish-trust note:
    v218 is the current-tree trusted BEST on the tracked baseline_hh surface.
    It preserves the accepted v217 long four-bay and runtime-cliff behavior,
    then adds one bounded dense four-bay deep-chain specialist that lowers
    residual first20 T on the prob_11/prob_13 subtype pocket without opening
    new regressions on the accepted surface.
"""

from alg_versions import reboot_v218_20260627_trackA_dense_fourbay_deep_chain_on_v217 as active


ACTIVE_VERSION = "reboot_v218_20260627_trackA_dense_fourbay_deep_chain_on_v217"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
