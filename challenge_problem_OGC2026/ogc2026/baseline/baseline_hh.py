"""HH active submission wrapper.

Current active working line:
    direct standard-import surface on
    reboot_v304_20260629_trackA_prob13like_subprocess_fallback_on_v298

Publish-trust note:
    v305 is the current-tree trusted BEST candidate on the tracked
    baseline_hh surface. It preserves the accepted v298 frozen line for all
    non-target rows, while promoting the accepted prob13-like subprocess-
    fallback specialist from v304.
"""

from __future__ import annotations

from alg_versions import (
    reboot_v304_20260629_trackA_prob13like_subprocess_fallback_on_v298 as active,
)


ACTIVE_VERSION = "reboot_v305_20260629_baseline_surface_direct_import_v304"


algorithm = active.algorithm
