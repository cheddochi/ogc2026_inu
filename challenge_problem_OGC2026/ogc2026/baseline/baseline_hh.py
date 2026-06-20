"""HH active submission wrapper.

Current active working line:
    reboot_v133_20260620_1705_prob40like_narrow_quantile_on_v132

Publish-trust note:
    v133 preserves the stabilized v132 surface and adds a safe prob40-like
    narrow quantile move that improves the full-train headline metrics.
"""

from alg_versions import reboot_v133_20260620_1705_prob40like_narrow_quantile_on_v132 as active


ACTIVE_VERSION = "reboot_v133_20260620_1705_prob40like_narrow_quantile_on_v132"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
