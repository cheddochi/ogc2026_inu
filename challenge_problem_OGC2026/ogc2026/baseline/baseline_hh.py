"""HH active submission wrapper.

Current active working line:
    reboot_v178_20260625_v142_specialist_slices_on_v177

Publish-trust note:
    v178 is now the strongest current-tree reproducible full40 line on the
    tracked wrapper surface. It keeps the v177 prob27 / Family B guard rows
    while recovering the live current-tree v142 signal on the prob31/prob32/
    prob37 specialist slices, and it now beats the old historical v142 full40
    evidence on both Total T and official objective.
"""

from alg_versions import reboot_v178_20260625_v142_specialist_slices_on_v177 as active


ACTIVE_VERSION = "reboot_v178_20260625_v142_specialist_slices_on_v177"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    return active.algorithm(prob_info, timelimit)
