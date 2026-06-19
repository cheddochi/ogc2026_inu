"""HH active submission wrapper.

Current active working line:
    reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116

Publish-trust note:
    Historical full-train evidence for v117 remains strong, but the fresh
    publish revalidation at
    reports/ogc2026_reboot_v001/verify_active_v117_publish_20260620_001/
    timed out on prob_31 and prob_37 under the active wrapper.
    Treat this file as the current recovery surface, not a freshly
    re-confirmed trusted accepted BEST for publish.
"""

from alg_versions import reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116 as active


ACTIVE_VERSION = "reboot_v117_20260620_0033_prob31like_concentrated_gap_on_v116"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
