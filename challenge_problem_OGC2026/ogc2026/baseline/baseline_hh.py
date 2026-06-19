"""HH active submission wrapper.

Current active working line:
    reboot_v122_20260620_0245_twobay_toptardy_quantile_reinsert_on_v117

Publish-trust note:
    v122 now has accepted full-train evidence at
    reports/ogc2026_reboot_v001/full_reboot_v122_train40_20260620_001/
    and fresh active publish revalidation at
    reports/ogc2026_reboot_v001/verify_active_v122_publish_20260620_001/
    with accepted_for_score 3/3 on prob_31, prob_37, and prob_40.
    Treat this file as the current trusted accepted BEST surface.
"""

from alg_versions import reboot_v122_20260620_0245_twobay_toptardy_quantile_reinsert_on_v117 as active


ACTIVE_VERSION = "reboot_v122_20260620_0245_twobay_toptardy_quantile_reinsert_on_v117"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
