#!/usr/bin/env python
"""Analyze trusted benchmark results by feature-based subtype.

This script combines a trusted readable benchmark CSV with train JSON features
and emits:
1. per-instance subtype table
2. aggregated subtype backlog summary
3. representative tier smoke recommendations

It is intentionally read-only with respect to algorithms: the goal is to
choose the next single-hypothesis candidate before touching baseline_hh again.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import pathlib
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class InstanceTier:
    label: str
    start: int
    end: int


TIERS = [
    InstanceTier("tier_01_04", 1, 4),
    InstanceTier("tier_05_08", 5, 8),
    InstanceTier("tier_09_12", 9, 12),
    InstanceTier("tier_13_16", 13, 16),
    InstanceTier("tier_17_20", 17, 20),
    InstanceTier("tier_21_25", 21, 25),
    InstanceTier("tier_26_30", 26, 30),
    InstanceTier("tier_31_35", 31, 35),
    InstanceTier("tier_36_40", 36, 40),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-csv", required=True, help="Readable benchmark CSV path.")
    parser.add_argument("--train-dir", required=True, help="Training JSON directory.")
    parser.add_argument("--out-dir", required=True, help="Output directory for analysis artifacts.")
    parser.add_argument(
        "--target-subtype-keyword",
        default="3bay/lowproc/runtime-risk",
        help="Keyword used to mark current hypothesis-target smoke rows.",
    )
    return parser.parse_args()


def mean(values: list[float]) -> float:
    return statistics.fmean(values) if values else 0.0


def pstdev(values: list[float]) -> float:
    return statistics.pstdev(values) if len(values) > 1 else 0.0


def quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    frac = pos - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def instance_number(instance_name: str) -> int:
    stem = pathlib.Path(instance_name).stem
    digits = "".join(ch for ch in stem if ch.isdigit())
    if not digits:
        raise ValueError(f"could not parse instance number from {instance_name}")
    return int(digits)


def tier_for_instance(number: int) -> str:
    for tier in TIERS:
        if tier.start <= number <= tier.end:
            return tier.label
    return "tier_other"


def block_tier(blocks: int) -> str:
    if blocks <= 200:
        return "small"
    if blocks <= 300:
        return "medium"
    return "large"


def proc_tier(proc_mean: float) -> str:
    if proc_mean >= 160:
        return "highproc"
    if proc_mean >= 80:
        return "midproc"
    return "lowproc"


def pref_tier(pref_conc: float) -> str:
    if pref_conc >= 0.68:
        return "concentrated"
    if pref_conc >= 0.50:
        return "moderate"
    return "diffuse"


def runtime_tier(runtime_sec: float) -> str:
    if runtime_sec >= 45:
        return "runtime-risk"
    if runtime_sec >= 25:
        return "runtime-mid"
    return "runtime-safe"


def t_pressure(t_value: float) -> str:
    if t_value >= 3000:
        return "high-T"
    if t_value >= 500:
        return "mid-T"
    if t_value > 0:
        return "low-T"
    return "T-zero"


def slack_tier(slack_q10: float, slack_min: float) -> str:
    if slack_min <= 0 and slack_q10 <= 5:
        return "tight"
    if slack_q10 <= 20:
        return "moderate"
    return "loose"


def workload_tier(work_std: float) -> str:
    if work_std >= 180:
        return "work-volatile"
    if work_std >= 100:
        return "work-mixed"
    return "work-stable"


def analyze_row(result_row: dict[str, str], problem_data: dict) -> dict[str, object]:
    blocks = problem_data["blocks"]
    bays = problem_data["bays"]

    proc = [float(block["processing_time"]) for block in blocks]
    rel = [float(block["release_time"]) for block in blocks]
    due = [float(block["due_date"]) for block in blocks]
    workload = [float(block["workload"]) for block in blocks]
    slack = [d - r - p for d, r, p in zip(due, rel, proc)]
    bay_areas = [float(bay["width"]) * float(bay["height"]) for bay in bays]

    pref_concentration = 0.0
    pref_gap_mean = 0.0
    feasible_pref_pressure = 0.0
    if blocks:
        best_bays = []
        gaps = []
        strong_pref_count = 0
        for block in blocks:
            prefs = [float(x) for x in block["bay_preferences"]]
            if prefs:
                best_idx = max(range(len(prefs)), key=lambda idx: prefs[idx])
                best_bays.append(best_idx)
                ordered = sorted(prefs, reverse=True)
                gap = ordered[0] - ordered[1] if len(ordered) > 1 else ordered[0]
                gaps.append(gap)
                if gap >= 50:
                    strong_pref_count += 1
        if best_bays:
            pref_concentration = Counter(best_bays).most_common(1)[0][1] / len(best_bays)
        pref_gap_mean = mean(gaps)
        feasible_pref_pressure = strong_pref_count / len(blocks)

    t_value = float(result_row["T"])
    runtime_sec = float(result_row["runtime_sec"])
    number = instance_number(result_row["instance"])

    row = {
        "instance": pathlib.Path(result_row["instance"]).stem,
        "instance_num": number,
        "tier": tier_for_instance(number),
        "blocks": len(blocks),
        "bays": len(bays),
        "objective": float(result_row["objective"]),
        "T": t_value,
        "L": float(result_row["L"]),
        "P": float(result_row["P"]),
        "runtime_sec": runtime_sec,
        "accepted_for_score": result_row["accepted_for_score"],
        "proc_mean": mean(proc),
        "proc_std": pstdev(proc),
        "proc_max": max(proc) if proc else 0.0,
        "release_span": (max(rel) - min(rel)) if rel else 0.0,
        "slack_mean": mean(slack),
        "slack_min": min(slack) if slack else 0.0,
        "slack_q10": quantile(slack, 0.10),
        "slack_q25": quantile(slack, 0.25),
        "slack_std": pstdev(slack),
        "work_mean": mean(workload),
        "work_std": pstdev(workload),
        "pref_concentration": pref_concentration,
        "pref_gap_mean": pref_gap_mean,
        "strong_pref_ratio": feasible_pref_pressure,
        "bay_area_mean": mean(bay_areas),
        "bay_area_total": sum(bay_areas),
    }

    row["block_tier"] = block_tier(int(row["blocks"]))
    row["proc_tier"] = proc_tier(float(row["proc_mean"]))
    row["pref_tier"] = pref_tier(float(row["pref_concentration"]))
    row["runtime_tier"] = runtime_tier(float(row["runtime_sec"]))
    row["t_pressure"] = t_pressure(float(row["T"]))
    row["slack_tier"] = slack_tier(float(row["slack_q10"]), float(row["slack_min"]))
    row["workload_tier"] = workload_tier(float(row["work_std"]))
    row["subtype"] = (
        f"{row['block_tier']}/{row['bays']}bay/{row['proc_tier']}/"
        f"{row['pref_tier']}/{row['runtime_tier']}/{row['slack_tier']}/{row['t_pressure']}"
    )
    row["family_key"] = (
        f"{row['block_tier']}/{row['bays']}bay/{row['proc_tier']}/{row['runtime_tier']}"
    )
    return row


def write_csv(path: pathlib.Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def choose_tier_smoke(rows: list[dict[str, object]], target_keyword: str) -> list[dict[str, object]]:
    picks: list[dict[str, object]] = []
    by_tier: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_tier[str(row["tier"])].append(row)

    for tier in TIERS:
        candidates = by_tier.get(tier.label, [])
        if not candidates:
            continue
        target_rows = [r for r in candidates if target_keyword in str(r["family_key"])]
        high_t_rows = [r for r in candidates if float(r["T"]) > 0]
        runtime_rows = sorted(candidates, key=lambda r: (-float(r["runtime_sec"]), -float(r["T"])))
        regression_rows = sorted(candidates, key=lambda r: (-float(r["P"]) - float(r["L"]), -float(r["T"])))

        chosen = None
        reason = ""
        if target_rows:
            chosen = sorted(target_rows, key=lambda r: (-float(r["T"]), -float(r["runtime_sec"])))[0]
            reason = "hypothesis-target"
        elif high_t_rows:
            chosen = sorted(high_t_rows, key=lambda r: (-float(r["T"]), -float(r["runtime_sec"])))[0]
            reason = "current-high-T"
        elif runtime_rows:
            chosen = runtime_rows[0]
            reason = "runtime-risk"
        else:
            chosen = regression_rows[0]
            reason = "regression-risk"

        picks.append(
            {
                "tier": tier.label,
                "instance": chosen["instance"],
                "reason": reason,
                "T": chosen["T"],
                "L": chosen["L"],
                "P": chosen["P"],
                "runtime_sec": chosen["runtime_sec"],
                "family_key": chosen["family_key"],
                "subtype": chosen["subtype"],
            }
        )
    return picks


def main() -> None:
    args = parse_args()
    results_csv = pathlib.Path(args.results_csv).resolve()
    train_dir = pathlib.Path(args.train_dir).resolve()
    out_dir = pathlib.Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    subtype_rows: list[dict[str, object]] = []
    with results_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for result_row in reader:
            instance = pathlib.Path(result_row["instance"]).stem
            problem_path = train_dir / f"{instance}.json"
            problem_data = json.loads(problem_path.read_text(encoding="utf-8"))
            subtype_rows.append(analyze_row(result_row, problem_data))

    subtype_rows.sort(key=lambda row: (int(row["instance_num"])))

    subtype_table_path = out_dir / "subtype_table.csv"
    subtype_fields = [
        "instance",
        "instance_num",
        "tier",
        "blocks",
        "bays",
        "objective",
        "T",
        "L",
        "P",
        "runtime_sec",
        "accepted_for_score",
        "block_tier",
        "proc_tier",
        "pref_tier",
        "runtime_tier",
        "slack_tier",
        "workload_tier",
        "t_pressure",
        "family_key",
        "subtype",
        "proc_mean",
        "proc_std",
        "proc_max",
        "release_span",
        "slack_mean",
        "slack_min",
        "slack_q10",
        "slack_q25",
        "slack_std",
        "work_mean",
        "work_std",
        "pref_concentration",
        "pref_gap_mean",
        "strong_pref_ratio",
        "bay_area_mean",
        "bay_area_total",
    ]
    write_csv(subtype_table_path, subtype_rows, subtype_fields)

    family_summary: list[dict[str, object]] = []
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in subtype_rows:
        grouped[str(row["family_key"])].append(row)

    for key, members in grouped.items():
        family_summary.append(
            {
                "family_key": key,
                "count": len(members),
                "avg_T": round(mean([float(m["T"]) for m in members]), 3),
                "sum_T": round(sum(float(m["T"]) for m in members), 3),
                "avg_runtime_sec": round(mean([float(m["runtime_sec"]) for m in members]), 3),
                "max_runtime_sec": round(max(float(m["runtime_sec"]) for m in members), 3),
                "nonzero_T_count": sum(1 for m in members if float(m["T"]) > 0),
                "high_T_count": sum(1 for m in members if float(m["T"]) >= 3000),
                "instances": ",".join(str(m["instance"]) for m in sorted(members, key=lambda x: int(x["instance_num"]))),
            }
        )
    family_summary.sort(key=lambda row: (-float(row["avg_T"]), -float(row["max_runtime_sec"]), row["family_key"]))

    family_summary_path = out_dir / "family_summary.csv"
    write_csv(
        family_summary_path,
        family_summary,
        [
            "family_key",
            "count",
            "avg_T",
            "sum_T",
            "avg_runtime_sec",
            "max_runtime_sec",
            "nonzero_T_count",
            "high_T_count",
            "instances",
        ],
    )

    smoke_rows = choose_tier_smoke(subtype_rows, args.target_subtype_keyword)
    smoke_path = out_dir / "representative_tier_smoke.csv"
    write_csv(
        smoke_path,
        smoke_rows,
        ["tier", "instance", "reason", "T", "L", "P", "runtime_sec", "family_key", "subtype"],
    )

    top_t_rows = sorted(subtype_rows, key=lambda row: (-float(row["T"]), -float(row["runtime_sec"])))[:12]
    multi_row_families = [row for row in family_summary if int(row["count"]) >= 2 and int(row["high_T_count"]) >= 1]
    next_family = None
    if multi_row_families:
        next_family = sorted(
            multi_row_families,
            key=lambda row: (
                -int(row["high_T_count"]),
                -int(row["count"]),
                -float(row["avg_T"]),
                -float(row["max_runtime_sec"]),
            ),
        )[0]
    elif family_summary:
        next_family = family_summary[0]

    summary = {
        "results_csv": str(results_csv),
        "train_dir": str(train_dir),
        "target_subtype_keyword": args.target_subtype_keyword,
        "top_t_instances": [row["instance"] for row in top_t_rows],
        "next_family": next_family,
        "representative_tier_smoke": smoke_rows,
    }
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report_lines = [
        "# v142 subtype backlog analysis",
        "",
        f"- source readable CSV: `{results_csv}`",
        f"- train dir: `{train_dir}`",
        f"- target keyword for next hypothesis smoke: `{args.target_subtype_keyword}`",
        "",
        "## Top T backlog",
        "",
        "| instance | T | L | P | runtime_sec | family_key | subtype |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in top_t_rows:
        report_lines.append(
            f"| {row['instance']} | {float(row['T']):.0f} | {float(row['L']):.0f} | "
            f"{float(row['P']):.0f} | {float(row['runtime_sec']):.2f} | "
            f"{row['family_key']} | {row['subtype']} |"
        )

    report_lines.extend(
        [
            "",
            "## Family summary",
            "",
            "| family_key | count | avg_T | high_T_count | nonzero_T_count | max_runtime_sec | instances |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in family_summary[:12]:
        report_lines.append(
            f"| {row['family_key']} | {row['count']} | {float(row['avg_T']):.1f} | "
            f"{row['high_T_count']} | {row['nonzero_T_count']} | {float(row['max_runtime_sec']):.2f} | "
            f"{row['instances']} |"
        )

    report_lines.extend(
        [
            "",
            "## Representative block-tier smoke candidates",
            "",
            "| tier | instance | reason | T | runtime_sec | family_key |",
            "| --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for row in smoke_rows:
        report_lines.append(
            f"| {row['tier']} | {row['instance']} | {row['reason']} | "
            f"{float(row['T']):.0f} | {float(row['runtime_sec']):.2f} | {row['family_key']} |"
        )

    if next_family:
        report_lines.extend(
            [
                "",
                "## Suggested next subtype",
                "",
                f"- family_key: `{next_family['family_key']}`",
                f"- avg T: `{float(next_family['avg_T']):.1f}`",
                f"- max runtime: `{float(next_family['max_runtime_sec']):.2f}s`",
                f"- members: `{next_family['instances']}`",
                "- rationale: prefers repeated high-T families with at least two members before single-row outliers under the plateau/T-zero-first contract.",
            ]
        )

    (out_dir / "analysis.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
