"""HH active submission wrapper.

Current active working line:
    reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122

Publish-trust note:
    v123 now has accepted full-train evidence at
    reports/ogc2026_reboot_v001/full_reboot_v123_train40_20260620_003/
    and refreshed wrapper/active-path revalidation at
    reports/ogc2026_reboot_v001/verify_active_v123_publish_20260620_002/.
    Treat this file as the current trusted accepted BEST surface.
"""

from alg_versions import reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122 as active


ACTIVE_VERSION = "reboot_v123_20260620_0915_threebay_highproc_prefix_repair_on_v122"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
