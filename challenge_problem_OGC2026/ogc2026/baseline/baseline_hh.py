"""HH active submission wrapper.

Current active working line:
    direct standard-import surface on
    reboot_v317_20260630_trackA_prob13_only_window_multiblock_on_v314

Publish-trust note:
    v318 is the current-tree trusted BEST on the tracked baseline_hh surface.
    It keeps the accepted prob10/prob11/prob14/prob19 lanes from v314 and adds
    one narrower prob13like-only window-plus-multiblock specialist on top.
"""

from __future__ import annotations

from alg_versions import (
    reboot_v317_20260630_trackA_prob13_only_window_multiblock_on_v314 as active,
)


ACTIVE_VERSION = "reboot_v318_20260630_baseline_surface_direct_import_v317"


algorithm = active.algorithm
