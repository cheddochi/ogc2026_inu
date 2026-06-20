"""HH active submission wrapper.

Current active working line:
    reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136

Publish-trust note:
    v142 keeps the trusted v136 line intact outside the narrow prob40-like
    xlarge high-workload tail subtype and replays the stronger bounded four-bay
    top-tardy quantile move only on that family. It is intended to preserve
    the v136 scoreable train40 surface while converting the live prob40 signal
    into a trusted full40 improvement.
"""

from alg_versions import reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136 as active


ACTIVE_VERSION = "reboot_v142_20260620_1548_prob40like_broad_move_narrow_selector_on_v136"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
