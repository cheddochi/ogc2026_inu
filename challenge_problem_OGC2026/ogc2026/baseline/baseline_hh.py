"""HH active submission wrapper.

Current active working line:
    reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132

Publish-trust note:
    v135 keeps the trusted v132 recovery line as its warm start and lowers only
    the prob40-like headroom gate. It is intended to preserve v132 stability
    while making the accepted prob40 improvement repeat more reliably.
"""

from alg_versions import reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132 as active


ACTIVE_VERSION = "reboot_v135_20260620_2105_prob40like_headroom_relax_on_v132"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
