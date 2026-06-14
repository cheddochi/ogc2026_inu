#!/usr/bin/env python3
"""Render an OGC2026 batch-test result (results.csv) as a markdown table and
a PNG image styled like the "OGC 2026 Training Benchmark" report cards.

Usage:
    python3 tools/ogc_report.py --out-dir reports/ogc_batch/<run> \
        --title "OGC 2026 Training Benchmark - <label>" \
        --png reports/ogc_batch/<run>/report.png
"""

import argparse
import csv
import json
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def repo_root_from_here() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def natural_key(name: str):
    parts = []
    token = ""
    for ch in name:
        if ch.isdigit():
            token += ch
        else:
            if token:
                parts.append(int(token))
                token = ""
            parts.append(ch)
    if token:
        parts.append(int(token))
    return parts


def load_rows(out_dir: pathlib.Path, repo_root: pathlib.Path):
    csv_path = out_dir / "results.csv"
    rows = []
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    rows.sort(key=lambda r: natural_key(r["problem"]))

    train_dir = repo_root / "challenge_problem_OGC2026" / "train"
    out = []
    for row in rows:
        prob_path = train_dir / row["problem"]
        n_bays = None
        if prob_path.exists():
            with prob_path.open(encoding="utf-8") as f:
                prob_info = json.load(f)
            n_bays = len(prob_info.get("bays", []))

        def to_float(key):
            v = row.get(key)
            try:
                return float(v)
            except (TypeError, ValueError):
                return None

        out.append(
            {
                "instance": pathlib.Path(row["problem"]).stem,
                "blocks": row.get("blocks") or "",
                "bays": n_bays if n_bays is not None else "",
                "objective": to_float("objective"),
                "T": to_float("obj1"),
                "L": to_float("obj2"),
                "P": to_float("obj3"),
                "runtime": to_float("wall_time"),
                "feasible": row.get("feasible") == "True",
                "stage": row.get("stage"),
            }
        )
    return out


def build_summary(rows, summary_json):
    n = len(rows)
    feasible = sum(1 for r in rows if r["feasible"])
    total_obj = sum(r["objective"] for r in rows if r["objective"] is not None)
    total_t = sum(r["T"] for r in rows if r["T"] is not None)
    runtimes = [r["runtime"] for r in rows if r["runtime"] is not None]
    avg_rt = sum(runtimes) / len(runtimes) if runtimes else 0.0
    max_rt = max(runtimes) if runtimes else 0.0
    return {
        "feasible": feasible,
        "total": n,
        "total_objective": total_obj,
        "total_t": total_t,
        "avg_runtime": avg_rt,
        "max_runtime": max_rt,
        "timelimit": summary_json.get("timelimit"),
        "alg_folder": summary_json.get("alg_folder"),
    }


def fmt_num(v, decimals=0):
    if v is None:
        return ""
    if decimals == 0:
        return f"{v:,.0f}"
    return f"{v:,.{decimals}f}"


def write_markdown(rows, summary, title, note, md_path: pathlib.Path):
    lines = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(
        f"**Feasible {summary['feasible']}/{summary['total']}** | "
        f"Total Objective {fmt_num(summary['total_objective'])} | "
        f"Total T {fmt_num(summary['total_t'])} | "
        f"Avg Runtime {summary['avg_runtime']:.2f}s | "
        f"Max Runtime {summary['max_runtime']:.2f}s | "
        f"timelimit={summary['timelimit']}s"
    )
    if note:
        lines.append("")
        lines.append(f"_{note}_")
    lines.append("")
    lines.append("| Instance | Blocks | Bays | Objective | T | L | P | Runtime |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in rows:
        status = "" if r["feasible"] else f" ⚠️{r['stage']}"
        lines.append(
            f"| {r['instance']}{status} | {r['blocks']} | {r['bays']} | "
            f"{fmt_num(r['objective'])} | {fmt_num(r['T'])} | "
            f"{fmt_num(r['L'], 1)} | {fmt_num(r['P'])} | "
            f"{r['runtime']:.2f}s |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_png(rows, summary, title, note, png_path: pathlib.Path):
    n_rows = len(rows)
    fig_h = 1.6 + 0.34 * n_rows
    fig, ax = plt.subplots(figsize=(10.5, fig_h))
    ax.axis("off")

    ax.text(0, 1, title, fontsize=18, weight="bold", va="top", family="sans-serif")

    subtitle = (
        f"Feasible {summary['feasible']}/{summary['total']}   "
        f"Total Objective {fmt_num(summary['total_objective'])}   "
        f"Total T {fmt_num(summary['total_t'])}   "
        f"Avg Runtime {summary['avg_runtime']:.2f}s   "
        f"Max Runtime {summary['max_runtime']:.2f}s"
    )
    ax.text(0, 0.955, subtitle, fontsize=10.5, va="top", color="#555555", family="sans-serif",
            transform=ax.transAxes)

    if note:
        ax.text(
            0.5, 0.915, note, fontsize=9.5, va="top", ha="center",
            color="#1a7a3a", family="sans-serif", transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.4", fc="#e6f7ec", ec="none"),
        )

    columns = ["Instance", "Blocks", "Bays", "Objective", "T", "L", "P", "Runtime"]
    cell_text = []
    for r in rows:
        cell_text.append(
            [
                r["instance"],
                str(r["blocks"]),
                str(r["bays"]),
                fmt_num(r["objective"]),
                fmt_num(r["T"]),
                fmt_num(r["L"], 1),
                fmt_num(r["P"]),
                f"{r['runtime']:.2f}s",
            ]
        )

    table = ax.table(
        cellText=cell_text,
        colLabels=columns,
        cellLoc="right",
        colLoc="right",
        loc="upper left",
        bbox=[0.0, 0.0, 1.0, 0.86],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9.5)

    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#e0e0e0")
        if r == 0:
            cell.set_facecolor("#1e2330")
            cell.set_text_props(color="white", weight="bold")
            cell.set_height(cell.get_height() * 1.2)
        else:
            row = rows[r - 1]
            cell.set_facecolor("#f4f6fa" if r % 2 == 0 else "#ffffff")
            if c == 0:
                cell.set_text_props(ha="left")
            # color T column by tardiness severity
            if columns[c] == "T":
                t = row["T"] or 0
                if t == 0:
                    cell.set_text_props(color="#1a7a3a")
                elif t <= 5:
                    cell.set_text_props(color="#c97a00")
                else:
                    cell.set_text_props(color="#c0392b")
            if columns[c] == "Runtime":
                rt = row["runtime"] or 0
                cell.set_text_props(color="#1a7a3a" if rt < 15 else "#c97a00")
            if not row["feasible"] and columns[c] == "Instance":
                cell.set_text_props(color="#c0392b", weight="bold")

    fig.tight_layout()
    fig.savefig(png_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", required=True, help="ogc_batch_test output dir")
    p.add_argument("--title", default="OGC 2026 Training Benchmark")
    p.add_argument("--note", default="")
    p.add_argument("--png", default=None)
    p.add_argument("--md", default=None)
    return p.parse_args()


def main():
    args = parse_args()
    repo_root = repo_root_from_here()
    out_dir = pathlib.Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = repo_root / out_dir

    rows = load_rows(out_dir, repo_root)
    summary_json = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))["summary"]
    summary = build_summary(rows, summary_json)

    md_path = pathlib.Path(args.md) if args.md else out_dir / "report.md"
    png_path = pathlib.Path(args.png) if args.png else out_dir / "report.png"

    write_markdown(rows, summary, args.title, args.note, md_path)
    write_png(rows, summary, args.title, args.note, png_path)

    print(f"wrote {md_path}")
    print(f"wrote {png_path}")


if __name__ == "__main__":
    main()
