"""reboot_v093_20260619_0917_threebay_midproc_slackband_on_v092.py

Strategy:
    Keep trusted v092 as the default path, then replay the previously useful
    3-bay mid-proc slack-band reinsertion family on top of the stabilized
    parent chain.

Metadata:
    version_id: reboot_v093_20260619_0917_threebay_midproc_slackband_on_v092
    parent_version: reboot_v092_20260619_0859_prob40like_runtime_stable_orient3
    status: accepted
    timestamp: 2026-06-19 09:17 KST
    strategy:
        - Preserve v092 unchanged outside the target family.
        - Build the trusted v092 warm start first.
        - On the target family, replay the bounded one-block reinsertion
          portfolio from v090 over the stabilized parent solution.
        - Keep only strictly better officially feasible results.
    hypothesis:
        v090's family repair already had a real signal on the 3-bay mid-proc
        slack-band rows, but it was rejected because the older parent chain
        still exposed hidden prob40 instability. Reusing the same family repair
        on top of the stable v092 parent should recover the local gains without
        reintroducing that hidden-risk regression.
    intended_metric_target:
        - improve the 3-bay mid-proc slack-band family
        - preserve the current 40/40 scoreable contract
        - improve avg objective versus trusted v092
    validation_status:
        accepted_for_score=40/40 on full train40 benchmark
    benchmark_evidence_path:
        reports/ogc2026_reboot_v001/full_reboot_v093_train40_20260619_001
    rollback_target: reboot_v092_20260619_0859_prob40like_runtime_stable_orient3
"""

from __future__ import annotations

import time

from alg_versions import reboot_v064_20260618_1715_threebay_diffuse_moderate_greedy_research as v064
from alg_versions import reboot_v090_20260619_0802_threebay_midproc_slackband_reinsert as v090
from alg_versions import reboot_v092_20260619_0859_prob40like_runtime_stable_orient3 as v092


ACTIVE_VERSION = "reboot_v093_20260619_0917_threebay_midproc_slackband_on_v092"


def algorithm(prob_info: dict, timelimit: float = 60) -> dict:
    """Preserve the official OGC2026 algorithm interface."""
    started = time.time()
    features = v064._selector_features(prob_info)
    tier = v064.v050._time_tier(float(timelimit))

    base_solution = v092.algorithm(prob_info, timelimit)
    base_result = v064.v001.check_feasibility(prob_info, base_solution)
    if (
        not base_result.get("feasible")
        or not v090._matches_threebay_midproc_slackband_family(features)
        or float(base_result.get("obj1") or 0.0) <= 0.0
    ):
        return base_solution

    remaining = max(0.0, float(timelimit) - (time.time() - started))
    if remaining <= 0.45:
        print(
            f"[baseline_hh reboot_v093] skip_threebay_midproc_slackband instance={prob_info.get('name')} "
            f"tier={tier} remaining={remaining:.2f}s"
        )
        return base_solution

    research_solution, research_result = v090._try_midproc_slackband_reinsert_portfolio(
        prob_info,
        base_solution,
        base_result,
        remaining,
        tier,
    )
    if v064._result_key(research_result) < v064._result_key(base_result):
        print(
            f"[baseline_hh reboot_v093] selected_threebay_midproc_slackband instance={prob_info.get('name')} "
            f"T={research_result.get('obj1')} objective={research_result.get('objective')}"
        )
        return research_solution

    print(
        f"[baseline_hh reboot_v093] keep_warm_start instance={prob_info.get('name')} "
        f"base_T={base_result.get('obj1')} cand_T={research_result.get('obj1')}"
    )
    return base_solution
