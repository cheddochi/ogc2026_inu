"""
run_all.py -- 전체 인스턴스 배치 테스트

사용법:
  python run_all.py                     # 현재 폴더 prob_*.json 전부
  python run_all.py --timelimit 120     # timelimit 변경
  python run_all.py --instances 1 2 5  # 특정 인스턴스만
"""

import json
import time
import argparse
import importlib
import sys
import os
import glob

# ── 인자 파싱 ──────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--timelimit",  type=float, default=60.0)
parser.add_argument("--instances",  type=int,   nargs="*")  # 없으면 전체
parser.add_argument("--json_dir",   type=str,   default=".")
args = parser.parse_args()

# ── 인스턴스 파일 수집 ──────────────────────────────────────────────────────
pattern = os.path.join(args.json_dir, "prob_*.json")
all_files = sorted(glob.glob(pattern))

if args.instances:
    all_files = [f for f in all_files
                 if any(f.endswith(f"prob_{i}.json") for i in args.instances)]

if not all_files:
    print(f"[ERROR] {pattern} 에서 파일을 찾을 수 없음")
    sys.exit(1)

print(f"총 {len(all_files)}개 인스턴스  timelimit={args.timelimit}s")
print("=" * 80)

# ── myalgorithm 동적 로드 ──────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import myalgorithm
from utils import check_feasibility

# ── 결과 수집 ───────────────────────────────────────────────────────────────
results = []

for fpath in all_files:
    name = os.path.basename(fpath).replace(".json", "")
    with open(fpath, encoding="utf-8") as f:
        prob_info = json.load(f)
    prob_info["name"] = name

    print(f"\n{'─'*40}")
    print(f"▶  {name}  (blocks={len(prob_info['blocks'])}, bays={len(prob_info['bays'])})")
    print(f"{'─'*40}")

    t0  = time.time()
    try:
        sol = myalgorithm.algorithm(prob_info, args.timelimit)
        elapsed = time.time() - t0

        chk = check_feasibility(prob_info, sol)
        if chk["feasible"]:
            r = dict(name=name,
                     feasible=True,
                     obj=chk["objective"],
                     Z1=chk["obj1"],
                     Z2=chk["obj2"],
                     Z3=chk["obj3"],
                     elapsed=elapsed)
            print(f"✅ FEASIBLE  obj={r['obj']:.0f}  "
                  f"Z1={r['Z1']:.1f}  Z2={r['Z2']:.1f}  Z3={r['Z3']:.1f}  "
                  f"elapsed={elapsed:.2f}s")
        else:
            r = dict(name=name, feasible=False,
                     obj=None, Z1=None, Z2=None, Z3=None, elapsed=elapsed)
            print(f"❌ INFEASIBLE  stage={chk['stage']}  elapsed={elapsed:.2f}s")

    except Exception as e:
        elapsed = time.time() - t0
        r = dict(name=name, feasible=False,
                 obj=None, Z1=None, Z2=None, Z3=None, elapsed=elapsed)
        print(f"💥 CRASH: {e}  elapsed={elapsed:.2f}s")

    results.append(r)

# ── 최종 요약 ───────────────────────────────────────────────────────────────
print(f"\n{'='*80}")
print(f"{'SUMMARY':^80}")
print(f"{'='*80}")

header = f"{'instance':<12} {'feasible':>8} {'obj':>14} {'Z1':>8} {'Z2':>10} {'Z3':>8} {'time':>8}"
print(header)
print("-" * 80)

n_feasible = 0
t_sum = 0.0
obj_sum = 0.0

for r in results:
    feasible_str = "✅" if r["feasible"] else "❌"
    if r["feasible"]:
        n_feasible += 1
        t_sum   += r["Z1"]
        obj_sum += r["obj"]
        print(f"{r['name']:<12} {feasible_str:>8} {r['obj']:>14.0f} "
              f"{r['Z1']:>8.1f} {r['Z2']:>10.1f} {r['Z3']:>8.1f} "
              f"{r['elapsed']:>7.1f}s")
    else:
        print(f"{r['name']:<12} {feasible_str:>8} {'—':>14} "
              f"{'—':>8} {'—':>10} {'—':>8} {r['elapsed']:>7.1f}s")

print("-" * 80)
n = len(results)
print(f"{'TOTAL':<12} {n_feasible}/{n} feasible   "
      f"T_sum={t_sum:.0f}   obj_sum={obj_sum:.0f}")
print(f"벤치마크 참고: feasible 20/20, T_sum=257, avg_time=12.51s")
print("=" * 80)
