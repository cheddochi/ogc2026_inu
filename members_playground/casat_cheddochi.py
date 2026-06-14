# casat_cheddochi.py
# CP-SAT + Adaptive LNS + Gurobi MIP 통합 솔버
#
# 진입점:  algorithm(prob_info, timelimit)
# 호출처:  myalgorithm.py → casat_cheddochi.algorithm(prob_info, timelimit)
#
# 솔버 우선순위 (자동 폴백)
#   1순위  Gurobi MIP + LNS with MIP repair   (gurobipy + 라이선스)
#   2순위  CP-SAT + Adaptive LNS              (pip install ortools)
#   3순위  EDD Greedy + post-hoc repair        (의존성 없음)
#
# 설계 원칙
#   결정 변수 = (bay_id, entry_time) 만 탐색
#     → 탐색 공간: bay × time  (원본 bay×orient×(x,y)×time 대비 수십 배 축소)
#   공간 배치 (x, y, orient_idx) = 스케줄 확정 후 결정론적 후처리

import math
import time
import copy
import random
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from utils import Bay, Block, _bounding_box, _resolve_layers

# ── 솔버 가용성 체크 ─────────────────────────────────────────────────────────
try:
    import gurobipy as _gp
    from gurobipy import GRB as _GRB
    _HAS_GUROBI = True
except ImportError:
    _HAS_GUROBI = False

try:
    from ortools.sat.python import cp_model as _cp
    _HAS_ORTOOLS = True
except ImportError:
    _HAS_ORTOOLS = False

# ── 상수 ─────────────────────────────────────────────────────────────────────
_MIP_LIMIT      = 150    # 이하: 전체 MIP / 초과: LNS
_REPAIR_TLIMIT  = 2.0    # LNS 이터레이션당 Gurobi repair 제한 (초)
_REPAIR_MAX_K   = 40     # MIP repair 최대 블록 수 (초과 시 greedy 폴백)
_MIP_GAP        = 0.01   # Gurobi 최적성 갭 1%
_PHASE2_RESERVE = 5.0    # Phase 2(공간 배치) + 출력 빌더용 예약 시간 (초)
                          # deadline = t0 + timelimit - _PHASE2_RESERVE
                          # algorithm() 내 모든 단계가 이 데드라인을 준수한다.

# ── 실행 환경 제약 (4코어 CPU / 16 GB RAM) ────────────────────────────────────
_MAX_THREADS    = 4       # 모든 솔버의 최대 스레드 수
_MAX_MEM_GB     = 14      # 솔버 허용 메모리 상한 (GB)
                          # 16GB 전체 중 OS·Python 프로세스용 2GB 여유 확보
                          # Gurobi : NodefileStart + SoftMemLimit 으로 적용
                          # CP-SAT : max_memory_in_mb 으로 적용
_FEASIBLE_FIRST = False


# ═══════════════════════════════════════════════════════════════════════════════
# §1  기하 헬퍼
# ═══════════════════════════════════════════════════════════════════════════════

def _bbox(blk, oi):
    """(lx0, ly0, lx1, ly1) — 참조점 기준 바운딩박스."""
    layers = _resolve_layers(blk["shape"][oi]["layers"])
    verts  = [v for l in layers for v in l] if layers else [(0, 0), (1, 1)]
    return _bounding_box(verts)

def _col_w(blk, oi):
    """정수 열 폭 = ceil(바운딩박스 폭)."""
    lx0, _, lx1, _ = _bbox(blk, oi)
    return max(1, math.ceil(lx1 - lx0))


def _int_grid_fits(lx0, ly0, lx1, ly1, bay_w, bay_h):
    """
    정수 좌표 (px, py) 로 바운딩박스를 bay 안에 둘 수 있는지 확인.

    px + lx0 >= 0  및  px + lx1 <= bay_w 를 동시에 만족하는 정수 px가
    존재해야 한다 (마찬가지로 y에 대해서도).  즉
        ceil(-lx0) <= floor(bay_w - lx1)
    실수 폭(lx1-lx0)이 bay_w 이하라도, ceil/floor 라운딩 때문에
    정수 그리드 상에는 들어갈 자리가 없을 수 있다 (margin이 1 미만일 때).
    """
    px_lo, px_hi = math.ceil(-lx0 - 1e-9), math.floor(bay_w - lx1 + 1e-9)
    py_lo, py_hi = math.ceil(-ly0 - 1e-9), math.floor(bay_h - ly1 + 1e-9)
    return px_lo <= px_hi and py_lo <= py_hi


def _narrowest_orient(blk, bay_w, bay_h):
    """
    bay 에 들어가는 방향 중 가장 좁은 것. (orient_idx, col_width).

    정수 그리드 상에 배치 가능한 방향이 없으면 (= 이 블록을 이 bay에 절대
    배치할 수 없으면) col_width = bay_w + 1 (capacity 초과 sentinel) 을
    반환한다. 이렇게 하면 _conflict_pairs / AddCumulative / greedy 의
    "used + cw <= W" 체크가 항상 실패해, Phase 1이 이 (block,bay) 조합을
    선택하지 않도록 만든다 → _spatial 에서 "bay 자체에 안 맞음" 케이스 제거.
    """
    best_oi, best_cw = 0, float("inf")
    for oi in range(len(blk["shape"])):
        lx0, ly0, lx1, ly1 = _bbox(blk, oi)
        if _int_grid_fits(lx0, ly0, lx1, ly1, bay_w, bay_h):
            cw = math.ceil(lx1 - lx0)
            if cw < best_cw:
                best_cw, best_oi = cw, oi
    if best_cw == float("inf"):
        best_oi, best_cw = 0, int(bay_w) + 1  # capacity 초과 sentinel → 선택 방지
    return best_oi, best_cw

def _precompute_orients(prob_info):
    """(block_id, bay_id) → (orient_idx, col_width) 사전 계산."""
    blocks, bays = prob_info["blocks"], prob_info["bays"]
    return {
        (bi, b): _narrowest_orient(blocks[bi], bays[b]["width"], bays[b]["height"])
        for bi in range(len(blocks)) for b in range(len(bays))
    }


def _fits_bay(blk, bay_w, bay_h):
    """블록이 어떤 방향으로든 정수 그리드 상에서 (bay_w x bay_h) 안에 들어가면 True."""
    for oi in range(len(blk["shape"])):
        lx0, ly0, lx1, ly1 = _bbox(blk, oi)
        if _int_grid_fits(lx0, ly0, lx1, ly1, bay_w, bay_h):
            return True
    return False


def _feasible_bays(prob_info):
    """
    block_id → 해당 블록이 들어갈 수 있는 bay_id 집합.

    어떤 방향으로도 bay 크기에 맞지 않는 (block, bay) 조합은 Phase 1의
    모든 솔버/휴리스틱에서 배제한다 (CP-SAT in_b 강제 0, greedy 후보 제외 등).
    각 블록은 최소 한 개 이상의 bay에 들어맞는다고 가정한다
    (문제 인스턴스가 그렇게 보장되어야 함; 그렇지 않으면 가장 큰 bay로 폴백).
    """
    blocks, bays = prob_info["blocks"], prob_info["bays"]
    n, M = len(blocks), len(bays)
    result = {}
    for bi in range(n):
        feas = {b for b in range(M)
                if _fits_bay(blocks[bi], bays[b]["width"], bays[b]["height"])}
        if not feas:
            # 어떤 bay에도 안 맞음 (이론상 발생 안 함) → 가장 큰 bay로 폴백
            feas = {max(range(M), key=lambda b: bays[b]["width"] * bays[b]["height"])}
        result[bi] = feas
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# §2  목적함수 평가
# ═══════════════════════════════════════════════════════════════════════════════

def _objective(prob_info, sched):
    """obj = w1·Σtardiness + w2·workload_imbalance + w3·Σpref_penalty"""
    blocks = prob_info["blocks"]
    n_bays = len(prob_info["bays"])
    w1 = prob_info.get("weights", {}).get("w1", 1.0)
    w2 = prob_info.get("weights", {}).get("w2", 1.0)
    w3 = prob_info.get("weights", {}).get("w3", 1.0)
    loads, tard, pen = [0.0] * n_bays, 0.0, 0.0
    for bi, s in sched.items():
        b = s["bay_id"]
        loads[b] += blocks[bi]["workload"]
        tard     += max(0.0, s["exit_time"] - blocks[bi]["due_date"])
        prefs     = blocks[bi]["bay_preferences"]
        pen      += max(prefs) - prefs[b]
    imb = (max(loads) - min(loads)) if n_bays > 1 else 0.0
    return w1 * tard + w2 * imb + w3 * pen


# ═══════════════════════════════════════════════════════════════════════════════
# §3  Phase 0 — EDD warm start
# ═══════════════════════════════════════════════════════════════════════════════

def _warm_start(prob_info, orients, feasible_bays=None):
    """
    EDD 순서로 bay 배정.
    각 블록에 대해 선호도 높은 bay부터 순회하며
    누적 열 폭 합 ≤ bay 폭인 가장 이른 진입 슬롯을 선택한다.
    """
    blocks, bays = prob_info["blocks"], prob_info["bays"]
    if feasible_bays is None:
        feasible_bays = _feasible_bays(prob_info)
    n_bays = len(bays)
    w1     = prob_info.get("weights", {}).get("w1", 1.0)
    order  = sorted(range(len(blocks)),
                    key=lambda i: (blocks[i]["due_date"], blocks[i]["processing_time"]))
    timeline = [[] for _ in range(n_bays)]
    sched    = {}

    for bi in order:
        blk   = blocks[bi]
        r, p  = blk["release_time"], blk["processing_time"]
        prefs = blk["bay_preferences"]
        best_score, best = float("inf"), None

        for bay_id in sorted(range(n_bays), key=lambda j: prefs[j], reverse=True):
            _, cw = orients[(bi, bay_id)]
            W     = int(bays[bay_id]["width"])
            cands = sorted({r} | {e for _, e, _ in timeline[bay_id]})
            for t in cands:
                entry  = max(r, t)
                exit_t = entry + p
                used   = sum(cu for a, e, cu in timeline[bay_id]
                             if a < exit_t and e > entry)
                if used + cw <= W:
                    score = (w1 * max(0, exit_t - blk["due_date"])
                             + (max(prefs) - prefs[bay_id]))
                    if score < best_score:
                        best_score = score
                        best = (bay_id, entry, exit_t, cw)
                    break

        if best is None:                        # 빈 bay 구간 강제 배치
            feas   = feasible_bays.get(bi, set(range(n_bays))) or set(range(n_bays))
            bay_id = max(feas, key=lambda j: prefs[j])
            _, cw  = orients[(bi, bay_id)]
            entry  = r
            changed = True
            while changed:
                changed = False
                exit_t  = entry + p
                for a, e, _ in timeline[bay_id]:
                    if a < exit_t and e > entry:
                        entry = max(entry, e)
                        changed = True
                        break
            best = (bay_id, entry, exit_t, cw)

        bay_id, entry, exit_t, cw = best
        timeline[bay_id].append((entry, exit_t, cw))
        sched[bi] = {"block_id": bi, "bay_id": bay_id,
                     "entry_time": int(entry), "exit_time": int(exit_t)}
    return sched


# ═══════════════════════════════════════════════════════════════════════════════
# §4  충돌 쌍 사전 계산
# ═══════════════════════════════════════════════════════════════════════════════

def _conflict_pairs(prob_info, orients):
    """
    동시 거주 시 열 폭 합이 bay 폭을 초과하는 (i, j, [bays]) 목록.
    이 경우 시간 분리 제약이 필요하다.
    """
    blocks, bays = prob_info["blocks"], prob_info["bays"]
    n, M = len(blocks), len(bays)
    result = []
    for i in range(n):
        for j in range(i + 1, n):
            cbays = [b for b in range(M)
                     if orients[(i, b)][1] + orients[(j, b)][1] > int(bays[b]["width"])]
            if cbays:
                result.append((i, j, cbays))
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# §5  Phase 1a-G — Gurobi 전체 MIP  (n ≤ _MIP_LIMIT)
# ═══════════════════════════════════════════════════════════════════════════════

def _gurobi_mip(prob_info, warm, orients, tlimit):
    """
    연속 start[i] + 이진 x[i,b] + pairwise big-M 분리 제약.

    CP-SAT 대비 Gurobi 이점
      • start[i] 연속 → T가 커도 도메인 폭발 없음
      • LP 완화 + Gurobi cuts → 타이트한 하한
      • 병렬 branch-and-bound (Threads=8)
      • warm start가 분수 LP에 즉시 반영
    """
    import gurobipy as gp
    from gurobipy import GRB

    blocks, bays = prob_info["blocks"], prob_info["bays"]
    n, M = len(blocks), len(bays)
    w1 = prob_info.get("weights", {}).get("w1", 1.0)
    w2 = prob_info.get("weights", {}).get("w2", 1.0)
    w3 = prob_info.get("weights", {}).get("w3", 1.0)

    T  = (max(blk["due_date"] for blk in blocks) * 2
          + sum(blk["processing_time"] for blk in blocks))
    BM = float(T)

    m = gp.Model("bay_mip")
    m.setParam("TimeLimit",        tlimit)
    m.setParam("Threads",          _MAX_THREADS)           # CPU 4코어 제한
    m.setParam("MIPGap",           _MIP_GAP)
    m.setParam("OutputFlag",       1)
    m.setParam("Presolve",         2)
    m.setParam("Cuts",             2)
    m.setParam("Symmetry",         2)                      # 대칭성 공격적 제거 → 탐색 공간 축소
    m.setParam("Heuristics",       0.3)                    # 탐색 시간의 30% 를 MIP 휴리스틱에 할당 (기본 5%)
    m.setParam("RINS",             10)                     # 10노드마다 RINS 휴리스틱 실행 → 현재 해 개선 가속
    m.setParam("MIPFocus",         1)                      # 실현 가능 해 조기 확보 우선
    m.setParam("ImproveStartTime", max(1.0, tlimit * 0.2)) # timelimit 20% 이후 개선 집중 (0.3 → 0.2)
    m.setParam("NodefileStart",    _MAX_MEM_GB * 0.8)      # 11.2 GB 초과 시 디스크 기록 (0.6 → 0.8, RAM 최대 활용)
    try:
        m.setParam("SoftMemLimit", _MAX_MEM_GB)            # Gurobi 10+: 메모리 초과 시 최적화 중단 (GB)
    except gp.GurobiError:
        pass                                               # 구버전에서는 NodefileStart 만으로 제어

    # 결정 변수
    start = m.addVars(n,
                      lb=[float(blocks[i]["release_time"]) for i in range(n)],
                      ub=[BM] * n,
                      vtype=GRB.CONTINUOUS, name="s")
    end   = m.addVars(n, lb=0.0,
                      ub=[BM + blocks[i]["processing_time"] for i in range(n)],
                      vtype=GRB.CONTINUOUS, name="e")
    x     = m.addVars(n, M, vtype=GRB.BINARY, name="x")

    for i in range(n):
        m.addConstr(end[i] == start[i] + blocks[i]["processing_time"])
    m.addConstrs((gp.quicksum(x[i, b] for b in range(M)) == 1 for i in range(n)),
                 name="assign")

    # 누적 폭 제약 (pairwise 분리)
    conflicts = _conflict_pairs(prob_info, orients)
    print(f"[Gurobi MIP] n={n}  conflict_pairs={len(conflicts)}")
    z = m.addVars(len(conflicts), vtype=GRB.BINARY, name="z")  # z[k]=1: i가 j보다 먼저

    for k, (i, j, cbays) in enumerate(conflicts):
        for b in cbays:
            m.addConstr(end[i] <= start[j] + BM*(1-z[k]) + BM*(1-x[i,b]) + BM*(1-x[j,b]))
            m.addConstr(end[j] <= start[i] + BM*z[k]     + BM*(1-x[i,b]) + BM*(1-x[j,b]))

    # 목적함수 변수
    tard = m.addVars(n, lb=0.0, vtype=GRB.CONTINUOUS, name="td")
    m.addConstrs((tard[i] >= end[i] - blocks[i]["due_date"] for i in range(n)))

    wl_v = m.addVars(M, lb=0.0, vtype=GRB.CONTINUOUS, name="wl")
    m.addConstrs((wl_v[b] == gp.quicksum(blocks[i]["workload"] * x[i,b] for i in range(n))
                  for b in range(M)))
    max_wl = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="mxwl")
    min_wl = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="mnwl")
    m.addConstrs((max_wl >= wl_v[b] for b in range(M)))
    m.addConstrs((min_wl <= wl_v[b] for b in range(M)))

    pp = m.addVars(n, lb=0.0, vtype=GRB.CONTINUOUS, name="pp")
    for i in range(n):
        prefs = blocks[i]["bay_preferences"]; s_max = max(prefs)
        m.addConstr(pp[i] == gp.quicksum((s_max - prefs[b]) * x[i,b] for b in range(M)))

    m.setObjective(w1*gp.quicksum(tard) + w2*(max_wl-min_wl) + w3*gp.quicksum(pp),
                   GRB.MINIMIZE)

    # warm start hints
    for i in range(n):
        if i in warm:
            wb, we = warm[i]["bay_id"], float(warm[i]["entry_time"])
            start[i].Start = we
            end[i].Start   = we + blocks[i]["processing_time"]
            for b in range(M):
                x[i,b].Start = 1.0 if b == wb else 0.0
    for k, (i, j, _) in enumerate(conflicts):
        if i in warm and j in warm:
            z[k].Start = 1.0 if warm[i]["exit_time"] <= warm[j]["entry_time"] else 0.0

    m.optimize()

    if m.SolCount > 0:
        result = {}
        for i in range(n):
            b_best = max(range(M), key=lambda b: x[i,b].X)
            e_val  = start[i].X
            p      = blocks[i]["processing_time"]
            result[i] = {"block_id": i, "bay_id": b_best,
                         "entry_time": int(round(e_val)),
                         "exit_time":  int(round(e_val + p))}
        print(f"[Gurobi MIP] obj={m.ObjVal:.2f}  gap={m.MIPGap*100:.1f}%  t={m.Runtime:.1f}s")
        return result

    print("[Gurobi MIP] feasible 해 없음 → warm start 반환")
    return warm


# ═══════════════════════════════════════════════════════════════════════════════
# §6  Phase 1a-C — CP-SAT 전체 MIP  (n ≤ _MIP_LIMIT, Gurobi 없을 때)
# ═══════════════════════════════════════════════════════════════════════════════

def _cpsat_mip(prob_info, warm, orients, tlimit):
    """OR-Tools CP-SAT. AddCumulative로 열 폭 제약 표현."""
    from ortools.sat.python import cp_model

    blocks, bays = prob_info["blocks"], prob_info["bays"]
    n, M = len(blocks), len(bays)
    w1 = prob_info.get("weights", {}).get("w1", 1.0)
    w2 = prob_info.get("weights", {}).get("w2", 1.0)
    w3 = prob_info.get("weights", {}).get("w3", 1.0)

    cw = [min(orients[(i, b)][1] for b in range(M)) for i in range(n)]
    feasible_bays = _feasible_bays(prob_info)
    T  = (max(blocks[i]["due_date"] for i in range(n)) * 2
          + sum(blocks[i]["processing_time"] for i in range(n)))
    S  = 1000   # float → int 스케일

    mdl   = cp_model.CpModel()
    bay_v = [mdl.NewIntVar(0, M-1, f"b{i}") for i in range(n)]
    st_v  = [mdl.NewIntVar(blocks[i]["release_time"], T, f"s{i}") for i in range(n)]
    end_v = [mdl.NewIntVar(blocks[i]["release_time"] + blocks[i]["processing_time"],
                           T + blocks[i]["processing_time"], f"e{i}") for i in range(n)]
    for i in range(n):
        mdl.Add(end_v[i] == st_v[i] + blocks[i]["processing_time"])

    in_b = [[mdl.NewBoolVar(f"in{i}_{b}") for b in range(M)] for i in range(n)]
    for i in range(n):
        mdl.AddExactlyOne(in_b[i])
        for b in range(M):
            mdl.Add(bay_v[i] == b).OnlyEnforceIf(in_b[i][b])
            mdl.Add(bay_v[i] != b).OnlyEnforceIf(in_b[i][b].Not())
            if b not in feasible_bays[i]:
                mdl.Add(in_b[i][b] == 0)  # 어떤 방향으로도 bay b에 안 맞음 → 배정 금지

    for b in range(M):
        ivs, dems = [], []
        for i in range(n):
            p  = blocks[i]["processing_time"]
            iv = mdl.NewOptionalIntervalVar(st_v[i], p, end_v[i], in_b[i][b], f"iv{i}_{b}")
            ivs.append(iv)
            dems.append(cw[i])
        mdl.AddCumulative(ivs, dems, int(bays[b]["width"]))

    td_v = []
    for i in range(n):
        td = mdl.NewIntVar(0, T, f"td{i}")
        mdl.AddMaxEquality(td, [end_v[i] - blocks[i]["due_date"], mdl.NewConstant(0)])
        td_v.append(td)

    wls      = [round(blocks[i]["workload"] * S) for i in range(n)]
    total_wl = sum(wls) + 1
    wl_v     = [mdl.NewIntVar(0, total_wl, f"wl{b}") for b in range(M)]
    for b in range(M):
        mdl.Add(wl_v[b] == sum(wls[i] * in_b[i][b] for i in range(n)))
    mx_wl = mdl.NewIntVar(0, total_wl, "mx")
    mn_wl = mdl.NewIntVar(0, total_wl, "mn")
    mdl.AddMaxEquality(mx_wl, wl_v)
    mdl.AddMinEquality(mn_wl, wl_v)
    imb_v = mdl.NewIntVar(0, total_wl, "imb")
    mdl.Add(imb_v == mx_wl - mn_wl)

    pp_v = []
    for i in range(n):
        prefs = blocks[i]["bay_preferences"]; s_max = max(prefs)
        pp = mdl.NewIntVar(0, round(s_max * S) + 1, f"pp{i}")
        mdl.Add(pp == sum(round((s_max - prefs[b]) * S) * in_b[i][b] for b in range(M)))
        pp_v.append(pp)

    # imb_v, pp_v 는 wl_v/pp 스케일(S) 때문에 "S * 실제값" 단위이지만
    # td_v 는 실제값(정수 시간) 그대로다. 세 항의 상대 가중치가
    # _objective()의 w1*tard + w2*imb + w3*pen 과 일치하도록
    # td_v 항에도 S를 곱해 동일한 "S * 실제값" 스케일로 맞춘다.
    # (이전 버전은 td_v에 S를 곱하지 않아 tardiness가 1000배 과소평가되어
    #  CP-SAT가 워밍스타트보다 나쁜 "최적" 해를 반환하는 문제가 있었다.)
    mdl.Minimize(round(w1*S)*S*sum(td_v) + round(w2*S)*imb_v + round(w3*S)*sum(pp_v))

    for i in range(n):
        if i in warm:
            wb, we = warm[i]["bay_id"], warm[i]["entry_time"]
            mdl.AddHint(bay_v[i], wb)
            mdl.AddHint(st_v[i], we)
            for b in range(M):
                mdl.AddHint(in_b[i][b], 1 if b == wb else 0)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = tlimit
    solver.parameters.num_search_workers  = _MAX_THREADS          # CPU 4코어 제한
    solver.parameters.max_memory_in_mb    = _MAX_MEM_GB * 1024    # RAM 14 GB 제한
    solver.parameters.linearization_level = 2                     # LP 완화 강화 → 타이트한 하한 → 빠른 수렴
    solver.parameters.log_search_progress = False

    status = solver.Solve(mdl)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        result = {}
        for i in range(n):
            b = solver.Value(bay_v[i])
            e = solver.Value(st_v[i])
            p = blocks[i]["processing_time"]
            result[i] = {"block_id": i, "bay_id": b,
                         "entry_time": int(e), "exit_time": int(e + p)}
        print(f"[CP-SAT] {solver.StatusName(status)}  wall={solver.WallTime():.1f}s")
        return result

    print("[CP-SAT] feasible 해 없음 → warm start 반환")
    return warm


# ═══════════════════════════════════════════════════════════════════════════════
# §7  Greedy repair  (LNS 폴백 / Gurobi warm start 용)
# ═══════════════════════════════════════════════════════════════════════════════

def _greedy_repair(prob_info, fixed, to_place, orients, feasible_bays=None, order_mode="edd"):
    """
    Greedy 재배치. MIP repair의 warm start 및 폴백, LNS repair로 사용.

    order_mode:
      "edd"      - EDD(due_date, processing_time) 순서 (warm start와 동일).
      "shuffled" - to_place 를 무작위 순서로 섞은 뒤 배치.
                   destroy=k개를 항상 EDD 순서로 동일하게 재배치하면 warm start와
                   거의 같은 해로 수렴해 LNS가 개선을 찾지 못한다 (탐색 다양성 부족).
                   순서를 섞으면 같은 (bay,time) 슬롯 경쟁에서 다른 블록이 우선권을
                   얻어 다른 지역해를 탐색할 수 있다.
    """
    blocks, bays = prob_info["blocks"], prob_info["bays"]
    n_bays = len(bays)
    w1     = prob_info.get("weights", {}).get("w1", 1.0)
    if feasible_bays is None:
        feasible_bays = _feasible_bays(prob_info)

    timeline = [[] for _ in range(n_bays)]
    for bi, s in fixed.items():
        b  = s["bay_id"]
        cw = orients[(bi, b)][1]
        timeline[b].append((s["entry_time"], s["exit_time"], cw))

    sched = dict(fixed)
    if order_mode == "shuffled":
        order = list(to_place)
        random.shuffle(order)
    else:
        order = sorted(to_place,
                       key=lambda i: (blocks[i]["due_date"], blocks[i]["processing_time"]))

    for bi in order:
        blk   = blocks[bi]
        r, p  = blk["release_time"], blk["processing_time"]
        prefs = blk["bay_preferences"]
        best_score, best = float("inf"), None

        for bay_id in sorted(range(n_bays), key=lambda j: prefs[j], reverse=True):
            _, cw = orients[(bi, bay_id)]
            W     = int(bays[bay_id]["width"])
            cands = sorted({r} | {e for _, e, _ in timeline[bay_id]})
            for t in cands:
                entry  = max(r, t)
                exit_t = entry + p
                used   = sum(cu for a, e, cu in timeline[bay_id]
                             if a < exit_t and e > entry)
                if used + cw <= W:
                    score = (w1 * max(0, exit_t - blk["due_date"])
                             + (max(prefs) - prefs[bay_id]))
                    if score < best_score:
                        best_score = score
                        best = (bay_id, entry, exit_t, cw)
                    break

        if best is None:
            feas   = feasible_bays.get(bi, set(range(n_bays))) or set(range(n_bays))
            bay_id = max(feas, key=lambda j: prefs[j])
            _, cw  = orients[(bi, bay_id)]
            entry  = r
            changed = True
            while changed:
                changed = False
                exit_t  = entry + p
                for a, e, _ in timeline[bay_id]:
                    if a < exit_t and e > entry:
                        entry = max(entry, e)
                        changed = True
                        break
            best = (bay_id, entry, exit_t, cw)

        bay_id, entry, exit_t, cw = best
        timeline[bay_id].append((entry, exit_t, cw))
        sched[bi] = {"block_id": bi, "bay_id": bay_id,
                     "entry_time": int(entry), "exit_time": int(exit_t)}
    return sched


# ═══════════════════════════════════════════════════════════════════════════════
# §8  Gurobi MIP repair  (k블록 소형 서브문제)
# ═══════════════════════════════════════════════════════════════════════════════

def _gurobi_repair(prob_info, fixed, to_place, orients, tlimit=_REPAIR_TLIMIT):
    """
    k개 파괴 블록 전체를 소형 MIP로 동시 최적화.

    greedy repair 대비: EDD 순차 결정 → k블록 동시 최적화.
    warm start = greedy 해 → 대부분 수 ms 수렴.
    k > _REPAIR_MAX_K 면 greedy 폴백.

    제약
      repaired ↔ repaired: 충돌 쌍 pairwise 분리
      repaired ↔ fixed   : 고정 블록과 충돌 분리
    """
    import gurobipy as gp
    from gurobipy import GRB

    if not to_place:
        return dict(fixed)
    if len(to_place) > _REPAIR_MAX_K:
        return _greedy_repair(prob_info, fixed, to_place, orients)

    blocks, bays = prob_info["blocks"], prob_info["bays"]
    k, M = len(to_place), len(bays)
    w1 = prob_info.get("weights", {}).get("w1", 1.0)
    w2 = prob_info.get("weights", {}).get("w2", 1.0)
    w3 = prob_info.get("weights", {}).get("w3", 1.0)

    T  = (max(blk["due_date"] for blk in blocks) * 2
          + sum(blk["processing_time"] for blk in blocks))
    BM = float(T)

    m = gp.Model("repair")
    m.setParam("TimeLimit",     tlimit)
    m.setParam("OutputFlag",    0)
    m.setParam("Threads",       _MAX_THREADS)      # CPU 4코어 제한
    m.setParam("MIPFocus",      1)
    m.setParam("Cuts",          2)
    m.setParam("Heuristics",    0.5)               # 소형 MIP: 시간의 50% 를 휴리스틱에 → 빠른 feasible 해
    m.setParam("NodefileStart", _MAX_MEM_GB * 0.8) # B&B 노드 디스크 기록 임계값 (0.6 → 0.8)

    start = m.addVars(k,
                      lb=[float(blocks[bi]["release_time"]) for bi in to_place],
                      ub=[BM] * k,
                      vtype=GRB.CONTINUOUS, name="s")
    x     = m.addVars(k, M, vtype=GRB.BINARY, name="x")
    m.addConstrs((gp.quicksum(x[ki, b] for b in range(M)) == 1 for ki in range(k)))

    def _end(ki):
        return start[ki] + blocks[to_place[ki]]["processing_time"]

    # repaired ↔ repaired 충돌
    z_rep = {}
    for ki_a, bi_a in enumerate(to_place):
        for ki_b, bi_b in enumerate(to_place):
            if ki_a >= ki_b:
                continue
            cbays = [b for b in range(M)
                     if orients[(bi_a,b)][1] + orients[(bi_b,b)][1] > int(bays[b]["width"])]
            if not cbays:
                continue
            z_v = m.addVar(vtype=GRB.BINARY, name=f"zr_{ki_a}_{ki_b}")
            z_rep[(ki_a, ki_b)] = z_v
            for b in cbays:
                m.addConstr(_end(ki_a) <= start[ki_b] + BM*(1-z_v) + BM*(1-x[ki_a,b]) + BM*(1-x[ki_b,b]))
                m.addConstr(_end(ki_b) <= start[ki_a] + BM*z_v     + BM*(1-x[ki_a,b]) + BM*(1-x[ki_b,b]))

    # repaired ↔ fixed 충돌
    for ki, bi in enumerate(to_place):
        for fi, fs in fixed.items():
            fb = fs["bay_id"]
            fa = float(fs["entry_time"])
            fe = float(fs["exit_time"])
            if orients[(bi,fb)][1] + orients[(fi,fb)][1] <= int(bays[fb]["width"]):
                continue
            z_f = m.addVar(vtype=GRB.BINARY, name=f"zf_{ki}_{fi}")
            # z_f=1: repaired 블록이 fixed 블록보다 늦게 시작
            m.addConstr(start[ki]  >= fe - BM*(1-z_f) - BM*(1-x[ki,fb]))
            m.addConstr(_end(ki)   <= fa + BM*z_f     + BM*(1-x[ki,fb]))

    # 목적함수
    tard = m.addVars(k, lb=0.0, vtype=GRB.CONTINUOUS, name="td")
    m.addConstrs((tard[ki] >= _end(ki) - blocks[to_place[ki]]["due_date"]
                  for ki in range(k)))

    fixed_loads = [sum(blocks[fi]["workload"] for fi, fs in fixed.items()
                       if fs["bay_id"] == b) for b in range(M)]
    wl_v = m.addVars(M, lb=0.0, vtype=GRB.CONTINUOUS, name="wl")
    for b in range(M):
        m.addConstr(wl_v[b] == fixed_loads[b] +
                    gp.quicksum(blocks[to_place[ki]]["workload"] * x[ki,b]
                                for ki in range(k)))
    max_wl = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="mxwl")
    min_wl = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name="mnwl")
    m.addConstrs((max_wl >= wl_v[b] for b in range(M)))
    m.addConstrs((min_wl <= wl_v[b] for b in range(M)))

    pp = m.addVars(k, lb=0.0, vtype=GRB.CONTINUOUS, name="pp")
    for ki, bi in enumerate(to_place):
        prefs = blocks[bi]["bay_preferences"]; s_max = max(prefs)
        m.addConstr(pp[ki] == gp.quicksum((s_max-prefs[b]) * x[ki,b] for b in range(M)))

    m.setObjective(w1*gp.quicksum(tard) + w2*(max_wl-min_wl) + w3*gp.quicksum(pp),
                   GRB.MINIMIZE)

    # greedy warm start
    greedy = _greedy_repair(prob_info, fixed, to_place, orients)
    for ki, bi in enumerate(to_place):
        gs = greedy[bi]
        start[ki].Start = float(gs["entry_time"])
        for b in range(M):
            x[ki,b].Start = 1.0 if b == gs["bay_id"] else 0.0
    for (ki_a, ki_b), z_v in z_rep.items():
        bi_a, bi_b = to_place[ki_a], to_place[ki_b]
        z_v.Start = 1.0 if greedy[bi_a]["exit_time"] <= greedy[bi_b]["entry_time"] else 0.0

    m.optimize()

    if m.SolCount > 0:
        result = dict(fixed)
        for ki, bi in enumerate(to_place):
            b_best = max(range(M), key=lambda b: x[ki,b].X)
            e_val  = start[ki].X
            p      = blocks[bi]["processing_time"]
            result[bi] = {"block_id": bi, "bay_id": b_best,
                          "entry_time": int(round(e_val)),
                          "exit_time":  int(round(e_val + p))}
        return result

    return greedy   # MIP 실패 → greedy 폴백


def _worst_blocks(prob_info, sched, k, n):
    """
    Worst-first destroy: 지연(tardiness) 기여도가 높은 블록을 우선 선택.

    지연이 큰 블록부터 최대 k//2 개를 선택하고, 나머지는 무작위로 채운다.
    순수 무작위 destroy 대비 이터레이션당 목적함수 개선 폭이 크다.
    """
    blocks = prob_info["blocks"]
    ranked = sorted(
        range(n),
        key=lambda i: max(0.0, sched[i]["exit_time"] - blocks[i]["due_date"]),
        reverse=True,
    )
    n_worst = max(1, k // 2)
    chosen  = set(ranked[:n_worst])
    pool    = [i for i in range(n) if i not in chosen]
    if pool and len(chosen) < k:
        chosen |= set(random.sample(pool, min(k - len(chosen), len(pool))))
    return list(chosen)


# ═══════════════════════════════════════════════════════════════════════════════
# §9  Adaptive LNS  (n > _MIP_LIMIT)
# ═══════════════════════════════════════════════════════════════════════════════

def _adaptive_lns(prob_info, warm, orients, deadline, use_gurobi_repair, feasible_bays=None):
    """
    Adaptive LNS.

    use_gurobi_repair=True  → _gurobi_repair  (k블록 동시 최적화, 고품질)
    use_gurobi_repair=False → _greedy_repair  (greedy 순차, 고속)

    deadline : 절대 시각 (time.time() 기준).
               algorithm() 이 계산한 데드라인을 직접 받아
               repair 1회 시간도 이 경계를 넘지 않도록 제한한다.

    k 조정 전략
      성공     → k 감소 (intensification)
      patience 횟수 미개선 → best 복귀 + k 증가 (diversification)
      데드라인 임박(< 0.5초) → 즉시 종료, best 반환
    """
    n        = len(prob_info["blocks"])
    patience = 10 if use_gurobi_repair else 30
    k_min    = max(2, n // (5  if use_gurobi_repair else 20))
    k_max    = max(k_min + 2, n // (2 if use_gurobi_repair else 3))
    k        = max(k_min, n // (5 if use_gurobi_repair else 10))
    tag      = "LNS+Gurobi" if use_gurobi_repair else "LNS+greedy"

    # deepcopy 대신 경량 dict 복사 — schedule 값이 모두 정수/문자열이므로 shallow copy 안전
    _sched_copy = lambda s: {bi: dict(v) for bi, v in s.items()}

    current  = _sched_copy(warm)
    best     = _sched_copy(warm)
    best_obj = _objective(prob_info, best)
    cur_obj  = best_obj
    no_impr  = 0
    t0_lns   = time.time()
    it       = 0

    print(f"[{tag}] n={n}  k_init={k}  k_range=[{k_min},{k_max}]  obj={best_obj:.2f}")

    while True:
        remaining = deadline - time.time()   # 데드라인까지 남은 초 (절대 시각 기준)
        if remaining < 0.5:                  # 0.5초 미만 → 즉시 중단
            break

        # repair 1회 시간 = 남은 시간의 절반 또는 _REPAIR_TLIMIT 중 작은 값
        # 단, 새 이터레이션을 시작하기에 너무 짧으면 중단
        t_rep = min(_REPAIR_TLIMIT, remaining * 0.5) if use_gurobi_repair else 0.0
        if use_gurobi_repair and t_rep < 0.1:
            break

        # Destroy 전략: worst-first(지연 기여도 상위) 와 random 을 50/50 으로 혼합
        # worst-first 는 이터레이션당 개선 폭을 높이고,
        # random 은 탐색 다양성을 유지해 국소해 고착을 방지한다.
        if random.random() < 0.5:
            destroy = _worst_blocks(prob_info, current, min(k, n), n)
        else:
            destroy = random.sample(range(n), min(k, n))
        fixed = {i: current[i] for i in range(n) if i not in destroy}

        # greedy repair는 항상 EDD 순서로 동일하게 재배치하면 destroy 전과
        # 거의 같은 해로 수렴해 개선을 찾지 못한다 (관찰: 450+ iter, obj 불변).
        # 순서를 무작위로 섞어 탐색 다양성을 확보한다.
        repair_order = "shuffled" if (not use_gurobi_repair and random.random() < 0.7) else "edd"
        candidate = (_gurobi_repair(prob_info, fixed, destroy, orients, t_rep)
                     if use_gurobi_repair
                     else _greedy_repair(prob_info, fixed, destroy, orients, feasible_bays,
                                          order_mode=repair_order))
        cand_obj  = _objective(prob_info, candidate)

        if cand_obj < cur_obj:
            current  = candidate
            cur_obj  = cand_obj
            no_impr  = 0
            k        = max(k_min, k - 1)
            if cand_obj < best_obj:
                best     = _sched_copy(candidate)   # deepcopy → 경량 복사
                best_obj = cand_obj
                print(f"[{tag}] it={it:5d}  obj={best_obj:.2f}"
                      f"  k={k}  t={time.time()-t0_lns:.1f}s")
        else:
            no_impr += 1
            if no_impr >= patience:
                current  = _sched_copy(best)        # deepcopy → 경량 복사
                cur_obj  = best_obj
                k        = min(k_max, k + 2)
                no_impr  = 0
        it += 1

    print(f"[{tag}] done  it={it}  obj={best_obj:.2f}  t={time.time()-t0_lns:.1f}s")
    return best


# ═══════════════════════════════════════════════════════════════════════════════
# §10  Phase 2 — 열 기반 공간 배치 (후처리)
# ═══════════════════════════════════════════════════════════════════════════════

def _rects_overlap(a, b, eps=1e-6):
    """AABB overlap test (strict interior), a/b = (x0, y0, x1, y1)."""
    return a[0] < b[2] - eps and b[0] < a[2] - eps and a[1] < b[3] - eps and b[1] < a[3] - eps


def _spatial(prob_info, sched):
    """
    (bay_id, entry_time, exit_time) 확정 스케줄 → (x, y, orient_idx).

    bay별로 진입 시각 순 처리.  현재 블록과 시간적으로 겹치는(동시 거주)
    이미 배치된 블록들의 전체 바운딩박스(x AND y)를 피해 빈 자리에 배치한다.
    (단순 x-구간 패킹이 아니라 진짜 2D AABB 비충돌 배치.)

    실패(빈 자리 없음) 시 repair: entry_time을 충돌 블록들 중 가장 이른
    exit_time으로 미루고 재시도한다.  이렇게 미뤄진 entry_time은
    sched 자체에 반영되어 _build_solution 출력과 일치한다.
    Phase 1의 누적 폭 근사 제약이 보수적이므로 일반적으로 repair는
    드물게만 발생한다.
    """
    blocks, bays = prob_info["blocks"], prob_info["bays"]
    pos = {}

    for b in range(len(bays)):
        bay_w = bays[b]["width"]
        bay_h = bays[b]["height"]
        ids   = sorted((bi for bi in sched if sched[bi]["bay_id"] == b),
                       key=lambda i: (sched[i]["entry_time"], i))

        for bi in ids:
            n_orients = len(blocks[bi]["shape"])
            # 좁은(열 폭 작은) 방향부터 시도
            orient_order = sorted(range(n_orients), key=lambda o: _col_w(blocks[bi], o))

            while True:
                entry_i = sched[bi]["entry_time"]
                exit_i  = sched[bi]["exit_time"]

                # 시간적으로 겹치는 이미 배치된 블록들의 전체 AABB 수집
                actives = []  # (bj, (x0,y0,x1,y1), exit_time)
                for bj, (px_j, py_j, oj) in pos.items():
                    if sched[bj]["bay_id"] != b:
                        continue
                    if sched[bj]["entry_time"] < exit_i and sched[bj]["exit_time"] > entry_i:
                        lx0j, ly0j, lx1j, ly1j = _bbox(blocks[bj], oj)
                        actives.append((bj, (px_j + lx0j, py_j + ly0j,
                                              px_j + lx1j, py_j + ly1j),
                                        sched[bj]["exit_time"]))

                placed = False
                for oi in orient_order:
                    lx0, ly0, lx1, ly1 = _bbox(blocks[bi], oi)
                    if not _int_grid_fits(lx0, ly0, lx1, ly1, bay_w, bay_h):
                        continue

                    # 정수 좌표 후보: bay 원점과 활성 블록들의 우측/상단 경계(올림)
                    # px + lx0 >= 0  (bay 좌측 경계) 을 만족하는 최소값을 하한으로 사용
                    px_min = max(0, math.ceil(-lx0 - 1e-9))
                    py_min = max(0, math.ceil(-ly0 - 1e-9))
                    px_cands = sorted({px_min} | {math.ceil(a[1][2] - lx0 - 1e-9) for a in actives})
                    py_cands = sorted({py_min} | {math.ceil(a[1][3] - ly0 - 1e-9) for a in actives})

                    for px in px_cands:
                        if px < px_min:
                            continue
                        x0, x1 = px + lx0, px + lx1
                        if x1 > bay_w + 1e-6 or x0 < -1e-6:
                            continue
                        for py in py_cands:
                            if py < py_min:
                                continue
                            y0, y1 = py + ly0, py + ly1
                            if y1 > bay_h + 1e-6 or y0 < -1e-6:
                                continue
                            cand = (x0, y0, x1, y1)
                            if not any(_rects_overlap(cand, a[1]) for a in actives):
                                pos[bi] = (px, py, oi)
                                placed   = True
                                break
                        if placed:
                            break
                    if placed:
                        break

                if placed:
                    break

                # ── repair: 빈 자리가 없음 → entry_time을 미루고 재시도 ──
                if not actives:
                    # 활성 블록이 없는데도 배치 불가 → bay 자체에 못 들어감.
                    # bay 크기에 실제로 맞는 방향(없으면 orient_order[0])으로
                    # 원점에 강제 배치 (이론상 발생하지 않아야 함).
                    fit_oi = None
                    for oi in orient_order:
                        lx0, ly0, lx1, ly1 = _bbox(blocks[bi], oi)
                        if _int_grid_fits(lx0, ly0, lx1, ly1, bay_w, bay_h):
                            fit_oi = oi
                            break
                    if fit_oi is None:
                        fit_oi = orient_order[0]
                    lx0, ly0, _, _ = _bbox(blocks[bi], fit_oi)
                    pos[bi] = (max(0, math.ceil(-lx0)), max(0, math.ceil(-ly0)), fit_oi)
                    break

                new_entry = min(a[2] for a in actives)
                if new_entry <= entry_i:
                    new_entry = entry_i + 1  # 무한루프 방지 (이론상 발생 안 함)
                proc = blocks[bi]["processing_time"]
                sched[bi] = dict(sched[bi])
                sched[bi]["entry_time"] = new_entry
                sched[bi]["exit_time"]  = new_entry + proc
                # while 루프 재시도

    return pos


# ═══════════════════════════════════════════════════════════════════════════════
# §11  출력 빌더
# ═══════════════════════════════════════════════════════════════════════════════

def _build_solution(sched, pos):
    """check_feasibility 호환 {"operations": {시각: [op, ...]}} 변환."""
    buckets = {}
    for bi, s in sched.items():
        x, y, oi   = pos.get(bi, (0, 0, 0))
        t_in, t_out, bay = s["entry_time"], s["exit_time"], s["bay_id"]
        buckets.setdefault(t_out, []).append((0, "EXIT",  bi, bay, None, None, None))
        buckets.setdefault(t_in,  []).append((1, "ENTRY", bi, bay, x,    y,    oi))

    ops = {}
    for t in sorted(buckets):
        result = []
        for _, kind, bi, bay, x, y, oi in sorted(buckets[t], key=lambda r: (r[0], r[2])):
            op = {"type": kind, "block_id": bi, "bay_id": bay}
            if kind == "ENTRY":
                op.update({"x": x, "y": y, "orient_idx": oi})
            result.append(op)
        ops[str(t)] = result

    return {"operations": ops}


def _time_overlaps(a_entry, a_exit, b_entry, b_exit):
    return a_entry < b_exit and b_entry < a_exit


def _empty_bay_entry(schedule_in_bay, release_time, proc_time):
    entry = int(release_time)
    changed = True
    while changed:
        changed = False
        exit_t = entry + int(proc_time)
        for a, e in schedule_in_bay:
            if _time_overlaps(entry, exit_t, a, e):
                entry = max(entry, int(e))
                changed = True
    return entry


def _serial_feasible_solution(prob_info):
    """Official-tester-safe fallback: no time overlap inside the same bay."""
    blocks, bays = prob_info["blocks"], prob_info["bays"]
    bay_objs = [Bay.from_dict(d, i) for i, d in enumerate(bays)]
    n_bays = len(bays)
    bay_schedules = [[] for _ in range(n_bays)]
    sched = {}
    pos = {}
    order = sorted(
        range(len(blocks)),
        key=lambda i: (blocks[i]["due_date"], blocks[i]["processing_time"], i),
    )

    for bi in order:
        blk = blocks[bi]
        prefs = blk["bay_preferences"]
        best = None
        for bay_id in sorted(range(n_bays), key=lambda j: prefs[j], reverse=True):
            bay = bay_objs[bay_id]
            for oi in range(len(blk["shape"])):
                test = Block(block_id=bi, block_data=blk, x=0, y=0, orient_idx=oi)
                bb = test.bounding_rect()
                x = max(0, math.ceil(-bb[0]))
                y = max(0, math.ceil(-bb[1]))
                placed = Block(block_id=bi, block_data=blk, x=x, y=y, orient_idx=oi)
                if bay.contains_block(placed):
                    best = (bay_id, x, y, oi)
                    break
            if best is not None:
                break

        if best is None:
            bay_id = max(range(n_bays), key=lambda j: prefs[j])
            test = Block(block_id=bi, block_data=blk, x=0, y=0, orient_idx=0)
            bb = test.bounding_rect()
            x = max(0, min(math.ceil(-bb[0]), math.floor(bays[bay_id]["width"] - bb[2])))
            y = max(0, min(math.ceil(-bb[1]), math.floor(bays[bay_id]["height"] - bb[3])))
            best = (bay_id, x, y, 0)

        bay_id, x, y, oi = best
        entry = _empty_bay_entry(
            bay_schedules[bay_id],
            blk["release_time"],
            blk["processing_time"],
        )
        exit_t = entry + int(blk["processing_time"])
        bay_schedules[bay_id].append((entry, exit_t))
        sched[bi] = {
            "block_id": bi,
            "bay_id": bay_id,
            "entry_time": entry,
            "exit_time": exit_t,
        }
        pos[bi] = (int(x), int(y), oi)

    return _build_solution(sched, pos)


# ═══════════════════════════════════════════════════════════════════════════════
# §12  공개 진입점
# ═══════════════════════════════════════════════════════════════════════════════

def algorithm(prob_info, timelimit=60):
    """
    Bay scheduling 최적화 알고리즘.
    myalgorithm.py 에서 casat_cheddochi.algorithm(prob_info, timelimit) 으로 호출.

    시간 관리 설계
    ─────────────────────────────────────────────────────────────────
    deadline  = 현재 시각 + timelimit - _PHASE2_RESERVE
                Phase 2(공간 배치)·출력 빌더 실행 시간을 미리 예약한다.

    best_solution 체크포인트
      Phase 0 완료 직후: warm start 해 → best_solution 확보  ← 즉시 반환 가능
      Phase 1 완료 직후: 최적화 해  → best_solution 갱신

    각 단계별 시간 초과 처리
      Phase 0  항상 실행 (빠름, 수 ms).
      Phase 1  deadline 까지 남은 시간이 _MIN_PHASE1(2초) 미만이면 건너뜀.
               Gurobi/CP-SAT: TimeLimit 파라미터로 내부 제어.
               LNS          : deadline 을 직접 전달 → 이터레이션 수준 제어.
      Phase 2  best_solution 확정 후 항상 실행 (_PHASE2_RESERVE 안에서 완료).

    실행 흐름
    ─────────
    Phase 0  EDD warm start          (fast greedy, 항상 실행)
    Phase 1  솔버 자동 선택
             Gurobi 있음 + n ≤ 150  → Gurobi 전체 MIP  (연속 시간, LP 완화)
             Gurobi 있음 + n > 150  → LNS + Gurobi MIP repair
             OR-Tools 있음 + n ≤ 150 → CP-SAT (AddCumulative)
             OR-Tools 있음 + n > 150 → Adaptive LNS (greedy repair)
             둘 다 없음              → warm start 반환 후 baseline_greedy 폴백
    Phase 2  열 기반 공간 배치       (결정론적 후처리)

    설치
    ─────────
    pip install gurobipy   # 1순위 (Gurobi 라이선스 필요)
    pip install ortools    # 2순위 (무료)
    """
    t0       = time.time()
    n        = len(prob_info["blocks"])
    # Phase 2 + 출력 빌더를 위해 _PHASE2_RESERVE 초 예약
    # timelimit 이 짧은 경우 예약량을 10% 로 줄임 (최소 2초)
    reserve  = max(2.0, min(_PHASE2_RESERVE, timelimit * 0.10))
    deadline = t0 + timelimit - reserve      # 이 시각까지만 최적화 수행
    _MIN_PHASE1 = 2.0                        # Phase 1 시작 최소 잔여 시간 (초)

    def _t_left():
        """deadline 까지 남은 시간 (음수 = 이미 초과)."""
        return deadline - time.time()

    def _finalize(sched):
        """스케줄 dict → check_feasibility 호환 solution dict (Phase 2)."""
        pos = _spatial(prob_info, sched)
        return _build_solution(sched, pos)

    # 솔버 레이블
    if _HAS_GUROBI:
        label = "Gurobi MIP" if n <= _MIP_LIMIT else "LNS+Gurobi repair"
    elif _HAS_ORTOOLS:
        label = "CP-SAT" if n <= _MIP_LIMIT else "LNS+greedy"
    else:
        label = "EDD greedy (fallback)"

    print(f"\n[casat_cheddochi] {'═'*38}")
    print(f"[casat_cheddochi] n_blocks   = {n}")
    print(f"[casat_cheddochi] timelimit  = {timelimit}s  (reserve={reserve:.1f}s)")
    print(f"[casat_cheddochi] Gurobi={'O' if _HAS_GUROBI else 'X'}"
          f"  OR-Tools={'O' if _HAS_ORTOOLS else 'X'}")
    print(f"[casat_cheddochi] phase 1    = {label}")
    print(f"[casat_cheddochi] {'─'*38}")

    if _FEASIBLE_FIRST:
        print("[casat_cheddochi] feasible-first serial path")
        return _serial_feasible_solution(prob_info)

    # Gurobi / OR-Tools 모두 없으면 바로 baseline_greedy 폴백
    if not _HAS_GUROBI and not _HAS_ORTOOLS:
        print("[casat_cheddochi] 솔버 없음 → baseline_greedy 폴백")
        import baseline_greedy
        return baseline_greedy.greedyalgorithm(prob_info, timelimit)

    best_solution = None   # 언제든 반환 가능한 최선해 (체크포인트)

    try:
        # ── Phase 0: EDD warm start ────────────────────────────────────────
        orients = _precompute_orients(prob_info)
        feasible_bays = _feasible_bays(prob_info)
        warm    = _warm_start(prob_info, orients, feasible_bays)

        # 체크포인트 1: warm start 해 즉시 확보
        # Phase 1 도중 어떤 문제가 생겨도 이 해를 반환할 수 있다.
        # _finalize는 sched를 in-place로 (entry/exit_time repair) 수정하므로
        # _objective는 _finalize 호출 *이후*에 계산해야 실제 반환 해의 목적값과 일치한다.
        best_solution = _finalize(warm)
        best_obj_final = _objective(prob_info, warm)
        print(f"[casat_cheddochi] Phase 0  obj={best_obj_final:.2f}"
              f"  t={time.time()-t0:.2f}s  (checkpoint saved)")

        # ── 시간 가드: Phase 1 시작 가능 여부 확인 ─────────────────────────
        if _t_left() < _MIN_PHASE1:
            print(f"[casat_cheddochi] 시간 부족 ({_t_left():.1f}s < {_MIN_PHASE1}s)"
                  f" → Phase 1 건너뜀, warm start 해 반환")
            return best_solution

        # ── Phase 1: 스케줄 최적화 ─────────────────────────────────────────
        if _HAS_GUROBI:
            if n <= _MIP_LIMIT:
                # Gurobi TimeLimit 에 _t_left() 전달 → 내부에서 시간 제어
                sched = _gurobi_mip(prob_info, warm, orients, _t_left())
            else:
                # deadline 직접 전달 → LNS 이터레이션 수준 제어
                sched = _adaptive_lns(prob_info, warm, orients, deadline,
                                      use_gurobi_repair=True, feasible_bays=feasible_bays)
        else:  # _HAS_ORTOOLS
            if n <= _MIP_LIMIT:
                sched = _cpsat_mip(prob_info, warm, orients, _t_left())
            else:
                sched = _adaptive_lns(prob_info, warm, orients, deadline,
                                      use_gurobi_repair=False, feasible_bays=feasible_bays)

        # 체크포인트 2: Phase 1 최적화 해가 (post-spatial 기준) Phase 0보다
        # 실제로 더 좋을 때만 교체한다.  CP-SAT/LNS가 8초 안에 warm start보다
        # 못한 해를 반환하거나, _spatial repair로 악화되는 경우를 방지한다.
        phase1_solution = _finalize(sched)
        phase1_obj_final = _objective(prob_info, sched)
        print(f"[casat_cheddochi] Phase 1  obj={phase1_obj_final:.2f}"
              f"  (warm start obj={best_obj_final:.2f})"
              f"  t={time.time()-t0:.2f}s")
        if phase1_obj_final < best_obj_final:
            best_solution  = phase1_solution
            best_obj_final = phase1_obj_final
            print(f"[casat_cheddochi] Phase 1 채택 (checkpoint updated)")
        else:
            print(f"[casat_cheddochi] Phase 1 기각 → warm start 해 유지")

    except Exception as e:
        # Phase 1 도중 오류 발생 → 체크포인트 1 (warm start 해) 사용
        print(f"[casat_cheddochi] Phase 1 오류: {e}"
              f"  → checkpoint 해 반환 (t={time.time()-t0:.2f}s)")

    # ── Phase 2: 공간 배치는 best_solution 확보 과정에서 이미 수행됨 ─────────
    # _finalize() 가 _spatial + _build_solution 을 포함하므로 별도 Phase 2 없음.
    elapsed = time.time() - t0
    remaining_after = timelimit - elapsed
    print(f"[casat_cheddochi] done  total={elapsed:.2f}s"
          f"  (잔여={remaining_after:.2f}s / reserve={reserve:.1f}s)")
    print(f"[casat_cheddochi] {'═'*38}\n")
    return best_solution
