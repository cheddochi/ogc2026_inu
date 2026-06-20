"""HH active submission wrapper.

Current active working line:
    reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135

Publish-trust note:
    v136 keeps the trusted v135 line intact outside the targeted two-bay
    concentrated high-proc tail subtype and deepens only the bounded top-tardy
    single-reinsert search on that family. It is intended to preserve v135
    stability while converting the live prob25/prob27 tail signal into a
    scoreable train40 improvement.
"""

from alg_versions import reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135 as active


ACTIVE_VERSION = "reboot_v136_20260620_2335_twobay_deeper_toptardy_on_v135"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
