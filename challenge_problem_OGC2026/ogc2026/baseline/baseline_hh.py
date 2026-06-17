"""HH active submission wrapper.

Current trusted BEST:
    reboot_v039_20260617_1304_runtime_sensitive_budget_guard

The wrapper points at the latest accepted best evidenced in VERSION_LOG.md and
the trusted full-train40 reports.
"""

from alg_versions import reboot_v039_20260617_1304_runtime_sensitive_budget_guard as active


ACTIVE_VERSION = "reboot_v039_20260617_1304_runtime_sensitive_budget_guard"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
