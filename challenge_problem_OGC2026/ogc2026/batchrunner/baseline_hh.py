"""
baseline_hh.py -- Gurobi-Based Hybrid Algorithm

Phase 0: EDD greedy warmstart (초고속, Gurobi MIP start용)
Phase 1: Gurobi MIP - 베이 배정 + entry/exit 시간 최적화
         (공간/크레인 제약 없이 순수 스케줄링 최적화 → T 최소화)
Phase 2: 공간 배치 - Gurobi 스케줄 기반으로 (x,y,orient) 결정
         (크레인 체크 포함, 블록당 시간 제한)
Phase 3: 크레인 위반 repair (빈 베이 윈도우)

진입점: hhalgorithm(prob_info, timelimit)
"""

import math
import time
from utils import Bay, Block, check_entry, check_exit, check_collisions, \
                  check_feasibility, _resolve_layers, _bounding_box


# ─────────────────────────────────────────────────────────────────────────────
# 헬퍼
# ─────────────────────────────────────────────────────────────────────────────

def _block_bbox(block_data, orient_idx):
    raw = block_data["shape"][orient_idx]["layers"]
    layers = _resolve_layers(raw)
    if not layers:
        return (0.0, 0.0, 1.0, 1.0)
    return _bounding_box([v for l in layers for v in l])


def _block_size(block_data, orient_idx):
    bb = _block_bbox(block_data, orient_idx)
    return bb[2] - bb[0], bb[3] - bb[1]


def _time_overlaps(a0, a1, b0, b1):
    return a0 < b1 and b0 < a1


def _empty_bay_entry(schedule_in_bay, r_time, proc):
    entry = int(r_time)
    changed = True
    while changed:
        changed = False
        exit_t = entry + proc
        for a, e in schedule_in_bay:
            if _time_overlaps(entry, exit_t, a, e):
                entry = max(entry, e)
                changed = True
    return entry


def _candidate_positions(bay_w, bay_h, placed_blocks, blk_bb):
    lx0, ly0, lx1, ly1 = blk_bb
    blk_w = lx1 - lx0
    xs = {max(0, math.ceil(-lx0))}
    ys = {max(0, math.ceil(-ly0))}
    for b in placed_blocks:
        bb = b.bounding_rect()
        xs.add(math.ceil(bb[2] - lx0))
        ys.add(math.ceil(bb[3] - ly0))
    if placed_blocks:
        intervals = sorted((b.bounding_rect()[0], b.bounding_rect()[2])
                           for b in placed_blocks)
        merged, cursor = [], 0.0
        for s, e in intervals:
            if merged and s < merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], e))
            else:
                merged.append([s, e])
        cursor = 0.0
        for seg_s, seg_e in merged:
            if seg_s - cursor >= blk_w - 1e-6:
                gx = math.ceil(cursor - lx0)
                if gx >= 0 and gx + lx1 <= bay_w + 1e-6:
                    xs.add(gx)
            cursor = max(cursor, seg_e)
        gx = math.ceil(cursor - lx0)
        if gx >= 0 and gx + lx1 <= bay_w + 1e-6:
            xs.add(gx)

    candidates = []
    for x in sorted(xs):
        for y in sorted(ys):
            if x + lx1 <= bay_w + 1e-6 and y + ly1 <= bay_h + 1e-6:
                candidates.append((int(x), int(y)))

    # ── Wall Snap 정렬: 후보 집합은 그대로, 순서만 변경 ──────────────────
    # x 범위가 placed_blocks와 겹치지 않는 위치(크레인 수직 경로 확보)를 앞으로
    if placed_blocks and candidates:
        occ_x = [(b.bounding_rect()[0], b.bounding_rect()[2])
                 for b in placed_blocks]
        def _x_free(px):
            bx0, bx1 = px + lx0, px + lx1
            return all(bx1 <= ox0 + 1e-6 or bx0 >= ox1 - 1e-6
                       for ox0, ox1 in occ_x)
        free  = [c for c in candidates if     _x_free(c[0])]
        other = [c for c in candidates if not _x_free(c[0])]
        return free + other

    return candidates


def _wallsnap_pos(bay_w, bay_h, concurrent, blk_bbox):
    """
    Wall Snap: concurrent 블록들과 x 범위가 겹치지 않는 y=bottom 위치 후보.

    크레인은 수직으로만 이동하므로, 새 블록의 x 범위 위에
    concurrent 블록이 없으면 check_entry 통과 확률이 극대화된다.
    concurrent 블록들의 x 구간 사이 빈 공간을 찾아 y=최저값에 배치.
    """
    lx0, ly0, lx1, ly1 = blk_bbox
    bw = lx1 - lx0

    # ── y: 가능한 가장 낮은 정수 위치 ────────────────────────────────────
    py = max(0, math.ceil(-ly0))
    if py + ly1 > bay_h + 1e-6:
        # 정수 좌표로 y 방향이 bay_h 초과 → 불가
        return []

    # ── concurrent 블록 x 범위 수집 & 정렬 ──────────────────────────────
    x_intervals = sorted(
        (blk.bounding_rect()[0], blk.bounding_rect()[2])
        for blk in concurrent
    ) if concurrent else []

    # ── x 방향 빈 공간 탐색 ──────────────────────────────────────────────
    candidates = []
    cursor = 0.0

    for (x_s, x_e) in x_intervals:
        if x_s - cursor >= bw - 1e-6:
            px = max(0, math.ceil(cursor - lx0))
            if px + lx1 <= bay_w + 1e-6:
                candidates.append((int(px), int(py)))
        cursor = max(cursor, x_e)

    # 마지막 블록 오른쪽
    px = max(0, math.ceil(cursor - lx0))
    if px + lx1 <= bay_w + 1e-6:
        candidates.append((int(px), int(py)))

    return candidates


def _build_operations(assignments):
    buckets = {}
    for a in assignments:
        te, tx = int(a["entry_time"]), int(a["exit_time"])
        bid, bay = a["block_id"], a["bay_id"]
        buckets.setdefault(tx, []).append((0, "EXIT",  bid, bay, None, None, None))
        buckets.setdefault(te, []).append((1, "ENTRY", bid, bay, a["x"], a["y"], a["orient_idx"]))
    ops = {}
    for t in sorted(buckets):
        result = []
        for _, kind, bid, bay, x, y, oi in sorted(buckets[t], key=lambda r: (r[0], r[2])):
            op = {"type": kind, "block_id": bid, "bay_id": bay}
            if kind == "ENTRY":
                op.update({"x": x, "y": y, "orient_idx": oi})
            result.append(op)
        ops[str(t)] = result
    return ops


# ─────────────────────────────────────────────────────────────────────────────
# Phase 0: EDD greedy warmstart
# ─────────────────────────────────────────────────────────────────────────────

def _edd_warmstart(prob_info):
    """
    초고속 EDD greedy: entry=release_time, 베이는 선호도 기준.
    크레인 체크 없음. Gurobi MIP start용.
    """
    blocks    = prob_info["blocks"]
    bays_data = prob_info["bays"]
    n, m      = len(blocks), len(bays_data)

    order = sorted(range(n), key=lambda i: (blocks[i]["due_date"],
                                            blocks[i]["processing_time"]))
    bay_avail = [0] * m
    result = {}
    for bi in order:
        b     = blocks[bi]
        r, p  = b["release_time"], b["processing_time"]
        prefs = b["bay_preferences"]
        best_j, best_entry, best_tard = 0, r, float("inf")
        for j in range(m):
            entry  = max(r, bay_avail[j])
            exit_t = entry + p
            tard   = max(0.0, exit_t - b["due_date"])
            score  = tard * 1e9 + exit_t * 1e3 - prefs[j]
            if score < best_tard:
                best_tard, best_j, best_entry = score, j, entry
        bay_avail[best_j] = best_entry + p
        result[bi] = {
            "block_id": bi, "bay_id": best_j,
            "entry_time": int(best_entry), "exit_time": int(best_entry + p),
            "x": 0, "y": 0, "orient_idx": 0
        }
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Phase 1: Gurobi MIP - 베이 배정 + 스케줄 최적화
# ─────────────────────────────────────────────────────────────────────────────

def _gurobi_schedule(prob_info, warmstart, gurobi_time):
    """
    Gurobi MIP: 베이 배정 + entry/exit 시간 최적화.
    공간/크레인 제약 없음 (Phase 2에서 처리).
    충돌 쌍 (둘이 같은 베이에 동시 있을 수 없는 블록 쌍) 은 BigM 분리 제약으로 처리.
    """
    try:
        import gurobipy as gp
        from gurobipy import GRB
    except ImportError:
        print("[HH] Gurobi 없음 → warmstart 사용")
        return warmstart

    blocks    = prob_info["blocks"]
    bays_data = prob_info["bays"]
    n, m      = len(blocks), len(bays_data)
    w1 = prob_info["weights"]["w1"]
    w2 = prob_info["weights"]["w2"]
    w3 = prob_info["weights"]["w3"]

    bay_areas = [b["width"] * b["height"] for b in bays_data]
    avg_area  = sum(bay_areas) / m
    u         = [avg_area / a for a in bay_areas]

    # 블록별 최소 폭 (방향 중 최소)
    min_w = []
    for bl in blocks:
        mw = min(_block_bbox(bl, oi)[2] - _block_bbox(bl, oi)[0]
                 for oi in range(len(bl["shape"])))
        min_w.append(max(0.1, mw))

    T_max = max(b["due_date"] for b in blocks) + max(b["processing_time"] for b in blocks) + 20
    BIG_M = T_max + 10

    model = gp.Model("OGC_schedule")
    model.setParam("TimeLimit",       gurobi_time)
    model.setParam("Threads",         4)
    model.setParam("MIPGap",          0.02)
    model.setParam("MIPFocus",        1)
    model.setParam("Cuts",            2)
    model.setParam("Presolve",        2)
    model.setParam("ImproveStartTime", gurobi_time * 0.3)
    model.setParam("OutputFlag",      1)

    # 변수
    x    = model.addVars(n, m, vtype=GRB.BINARY,  name="x")
    s    = model.addVars(n, lb=0, ub=T_max, vtype=GRB.INTEGER, name="s")
    tard = model.addVars(n, lb=0, name="tard")
    L    = model.addVars(m, lb=0, name="L")
    W    = model.addVar(lb=0, name="W")

    # 배정: 블록당 정확히 1개 베이
    for i in range(n):
        model.addConstr(gp.quicksum(x[i,j] for j in range(m)) == 1)

    # 가용일 제약
    for i in range(n):
        model.addConstr(s[i] >= blocks[i]["release_time"])

    # 납기 지연
    for i in range(n):
        model.addConstr(tard[i] >= s[i] + blocks[i]["processing_time"] - blocks[i]["due_date"])

    # 베이별 workload
    for j in range(m):
        model.addConstr(L[j] == gp.quicksum(
            blocks[i]["workload"] * x[i,j] for i in range(n)))

    # Workload 불균형
    for j1 in range(m):
        for j2 in range(j1+1, m):
            model.addConstr(W >= u[j1]*L[j1] - u[j2]*L[j2])
            model.addConstr(W >= u[j2]*L[j2] - u[j1]*L[j1])

    # ── 블록-베이 크기 호환성: 어떤 orientation으로도 맞지 않으면 배정 금지
    for i in range(n):
        for j in range(m):
            bw_j = bays_data[j]["width"]
            bh_j = bays_data[j]["height"]
            can_fit = any(
                (_block_bbox(blocks[i], oi)[2] - _block_bbox(blocks[i], oi)[0] <= bw_j + 1e-6 and
                 _block_bbox(blocks[i], oi)[3] - _block_bbox(blocks[i], oi)[1] <= bh_j + 1e-6)
                for oi in range(len(blocks[i]["shape"]))
            )
            if not can_fit:
                model.addConstr(x[i, j] == 0)

    # ── 충돌 쌍 제약: 2-way + density violation 기반 추가 쌍 ─────────────
    # 기존: min_w[i]+min_w[j] > bay_w 인 쌍에만 순서 부여 (2-way)
    # 추가: Phase 0 warmstart 기반으로 k개 블록이 동시 점유 시 총 min_w > bay_w
    #        → 그 중 (slack 최소, slack 최대) 쌍에 순서 제약 추가 (k-way→쌍 분해)
    conflict_set = {}  # (i1, i2, j) -> True  중복 방지

    # 기존 2-way 충돌 쌍
    for j in range(m):
        bw = bays_data[j]["width"]
        for i1 in range(n):
            for i2 in range(i1+1, n):
                if min_w[i1] + min_w[i2] > bw + 1e-6:
                    conflict_set[(i1, i2, j)] = True

    # density violation 기반 추가 쌍 (Phase 0 warmstart 시간축 sweep)
    if warmstart:
        for j in range(m):
            bw = bays_data[j]["width"]
            bay_bids = [i for i in range(n) if warmstart[i]["bay_id"] == j]
            events = sorted(
                [(warmstart[i]["entry_time"], 0, i) for i in bay_bids] +
                [(warmstart[i]["exit_time"],  1, i) for i in bay_bids]
            )
            active = set()
            for _, evt_type, bi in events:
                if evt_type == 1:
                    active.discard(bi)
                else:
                    active.add(bi)
                    if sum(min_w[i] for i in active) > bw + 1e-6 and len(active) >= 2:
                        # slack 기준 정렬: 작을수록 tight (먼저 처리), 클수록 여유
                        grp = sorted(active,
                                     key=lambda b: blocks[b]["due_date"] - warmstart[b]["exit_time"])
                        anchor = grp[0]   # slack 최소 → 뒤로 밀면 T 증가
                        victim = grp[-1]  # slack 최대 → 뒤로 밀어도 T 최소 영향
                        if anchor != victim:
                            i1d, i2d = min(anchor, victim), max(anchor, victim)
                            conflict_set[(i1d, i2d, j)] = True

    n_conflict = 0
    for (i1, i2, j) in conflict_set:
        P1, P2 = blocks[i1]["processing_time"], blocks[i2]["processing_time"]
        y = model.addVar(vtype=GRB.BINARY)
        model.addConstr(
            s[i1] + P1 <= s[i2]
            + BIG_M*(1-y)
            + BIG_M*(1-x[i1,j])
            + BIG_M*(1-x[i2,j])
        )
        model.addConstr(
            s[i2] + P2 <= s[i1]
            + BIG_M*y
            + BIG_M*(1-x[i1,j])
            + BIG_M*(1-x[i2,j])
        )
        n_conflict += 1

    print(f"[Gurobi] n={n}  m={m}  conflict_pairs={n_conflict}")

    # 선호도 페널티
    pref = gp.quicksum(
        (max(blocks[i]["bay_preferences"]) - blocks[i]["bay_preferences"][j]) * x[i,j]
        for i in range(n) for j in range(m)
    )

    model.setObjective(
        w1 * gp.quicksum(tard[i] for i in range(n)) + w2 * W + w3 * pref,
        GRB.MINIMIZE
    )

    # MIP start (warmstart)
    if warmstart:
        for i, a in warmstart.items():
            j = a["bay_id"]
            if 0 <= j < m:
                x[i, j].start = 1
                s[i].start    = a["entry_time"]

    # ── ICG: Iterative Constraint Generation ─────────────────────────────
    # 각 반복에서 Gurobi TimeLimit을 동적으로 줄여 전체 ICG가 gurobi_time 내에 완료
    icg_start = time.time()
    for icg_iter in range(15):
        elapsed_icg = time.time() - icg_start
        remaining   = gurobi_time - elapsed_icg
        if remaining < 1.0:
            break

        # 첫 반복: 시간 60% 사용 (초기 최적화), 이후: 남은 시간 30% 또는 최대 8초
        if icg_iter == 0:
            iter_limit = remaining * 0.60
        else:
            iter_limit = min(remaining * 0.35, 8.0)
        model.Params.TimeLimit = max(0.5, iter_limit)

        model.optimize()
        if model.SolCount == 0:
            break

        # 현재 솔루션 추출
        cur = {}
        for i in range(n):
            bid = next((j for j in range(m) if x[i,j].X > 0.5), 0)
            ent = max(blocks[i]["release_time"], int(round(s[i].X)))
            cur[i] = {"bay_id": bid, "entry_time": ent,
                      "exit_time": ent + blocks[i]["processing_time"]}

        # density violation 감지: min_w 기반 우선, 해소되면 x슬롯 기반으로 정밀 체크
        new_pairs     = []
        minw_violated = False

        for j in range(m):
            bw = bays_data[j]["width"]
            bh = bays_data[j]["height"]
            bay_bids = [i for i in range(n) if cur[i]["bay_id"] == j]

            # ── 방법 1: min_w 기반 density violation (빠름) ──────────────
            events = sorted(
                [(cur[i]["entry_time"], 0, i) for i in bay_bids] +
                [(cur[i]["exit_time"],  1, i) for i in bay_bids]
            )
            active = set()
            for _, evt_type, bi in events:
                if evt_type == 1:
                    active.discard(bi)
                else:
                    active.add(bi)
                    if sum(min_w[i] for i in active) > bw + 1e-6 and len(active) >= 2:
                        grp = sorted(active,
                                     key=lambda b: blocks[b]["due_date"] - cur[b]["exit_time"])
                        anchor, victim = grp[0], grp[-1]
                        if anchor != victim:
                            i1d, i2d = min(anchor, victim), max(anchor, victim)
                            if (i1d, i2d, j) not in conflict_set:
                                conflict_set[(i1d, i2d, j)] = True
                                new_pairs.append((i1d, i2d, j))
                                minw_violated = True

        # ── 방법 2: x슬롯 시뮬레이션 기반 (패턴3 해결) ──────────────────
        # min_w violation이 완전히 해소된 후에만 적용
        # (동시에 두 체크를 하면 제약이 너무 강해져서 feasibility 붕괴)
        if not minw_violated:
            for j in range(m):
                bw = bays_data[j]["width"]
                bh = bays_data[j]["height"]
                bay_bids = [i for i in range(n) if cur[i]["bay_id"] == j]
                bay_sched_j = {i: cur[i] for i in bay_bids}
                x_slots_j = _precompute_x_slots(bay_sched_j, blocks, bw, bh)
                xslot_added = 0
                for bi in sorted(bay_bids,
                                 key=lambda b: blocks[b]["due_date"] - cur[b]["exit_time"]):
                    if xslot_added >= 10:
                        break
                    if x_slots_j.get(bi) is not None:
                        continue
                    entry_i = cur[bi]["entry_time"]
                    exit_i  = cur[bi]["exit_time"]
                    concurrent = [bj for bj in bay_bids
                                  if bj != bi
                                  and cur[bj]["entry_time"] < exit_i
                                  and cur[bj]["exit_time"]  > entry_i]
                    if concurrent:
                        all_group = [bi] + concurrent
                        grp = sorted(all_group,
                                     key=lambda b: blocks[b]["due_date"] - cur[b]["exit_time"])
                        anchor, victim = grp[0], grp[-1]
                        if anchor != victim:
                            i1d, i2d = min(anchor, victim), max(anchor, victim)
                            if (i1d, i2d, j) not in conflict_set:
                                conflict_set[(i1d, i2d, j)] = True
                                new_pairs.append((i1d, i2d, j))
                                xslot_added += 1

        if not new_pairs:
            print(f"[ICG] iter={icg_iter+1}: no violation → done")
            break

        # 새 쌍 제약 추가 후 재최적화
        for (i1, i2, j) in new_pairs:
            P1, P2 = blocks[i1]["processing_time"], blocks[i2]["processing_time"]
            yv = model.addVar(vtype=GRB.BINARY)
            model.addConstr(s[i1]+P1 <= s[i2] + BIG_M*(1-yv) + BIG_M*(1-x[i1,j]) + BIG_M*(1-x[i2,j]))
            model.addConstr(s[i2]+P2 <= s[i1] + BIG_M*yv + BIG_M*(1-x[i1,j]) + BIG_M*(1-x[i2,j]))
            n_conflict += 1

        print(f"[ICG] iter={icg_iter+1}: +{len(new_pairs)} pairs  total={n_conflict}"
              f"  elapsed={time.time()-icg_start:.2f}s")

    if model.SolCount == 0:
        print("[Gurobi] 해 없음 → warmstart 반환")
        return warmstart

    result = {}
    for i in range(n):
        bay_id = next((j for j in range(m) if x[i,j].X > 0.5), 0)
        entry  = max(blocks[i]["release_time"], int(round(s[i].X)))
        result[i] = {
            "block_id":   i,
            "bay_id":     bay_id,
            "entry_time": entry,
            "exit_time":  entry + blocks[i]["processing_time"],
            "x": 0, "y": 0, "orient_idx": 0
        }
    obj_val = model.ObjVal
    print(f"[Gurobi] obj={obj_val:.1f}  gap={model.MIPGap*100:.1f}%")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Phase 2: 공간 배치 (Gurobi 스케줄 기반, 크레인 체크 포함)
# ─────────────────────────────────────────────────────────────────────────────

def _cpsat_schedule(prob_info, warmstart, timelimit):
    """
    CP-SAT으로 베이 배정 + entry/exit 시간 최적화.
    AddCumulative로 density 제약 직접 포함 → ICG 불필요.
    warmstart: 그리디 결과 {bi: {bay_id, entry_time, exit_time}}
    """
    try:
        from ortools.sat.python import cp_model
    except ImportError:
        print("[HH] ortools 없음 → warmstart 사용")
        return warmstart

    blocks_data = prob_info["blocks"]
    bays_data   = prob_info["bays"]
    n, m        = len(blocks_data), len(bays_data)
    w1          = prob_info["weights"]["w1"]

    # 블록별 최소 x폭 (정수)
    min_w = []
    for bl in blocks_data:
        mw = min(_block_bbox(bl, oi)[2] - _block_bbox(bl, oi)[0]
                 for oi in range(len(bl["shape"])))
        min_w.append(max(1, int(math.ceil(mw))))

    horizon = int(max(b["due_date"] for b in blocks_data) +
                  max(b["processing_time"] for b in blocks_data) + 30)

    model  = cp_model.CpModel()
    P_list = [int(math.ceil(blocks_data[i]["processing_time"])) for i in range(n)]
    R_list = [int(blocks_data[i]["release_time"]) for i in range(n)]
    D_list = [int(blocks_data[i]["due_date"])     for i in range(n)]

    bay   = [model.NewIntVar(0, m-1,   f'bay_{i}')   for i in range(n)]
    start = [model.NewIntVar(R_list[i], horizon, f's_{i}') for i in range(n)]
    end   = [model.NewIntVar(0, horizon, f'e_{i}')   for i in range(n)]
    tard  = [model.NewIntVar(0, horizon, f't_{i}')   for i in range(n)]

    for i in range(n):
        model.Add(end[i] == start[i] + P_list[i])
        model.Add(tard[i] >= end[i] - D_list[i])

    # 베이 크기 호환성
    for i in range(n):
        for j in range(m):
            bw_j = bays_data[j]["width"]
            bh_j = bays_data[j]["height"]
            can_fit = any(
                (_block_bbox(blocks_data[i], oi)[2] - _block_bbox(blocks_data[i], oi)[0] <= bw_j + 1e-6 and
                 _block_bbox(blocks_data[i], oi)[3] - _block_bbox(blocks_data[i], oi)[1] <= bh_j + 1e-6)
                for oi in range(len(blocks_data[i]["shape"]))
            )
            if not can_fit:
                model.Add(bay[i] != j)

    # density 제약: AddCumulative (핵심!)
    # 같은 베이에서 동시 점유 min_w 합 ≤ bay_w
    for j in range(m):
        bw_j       = int(bays_data[j]["width"])
        ivs_j, dems_j = [], []
        for i in range(n):
            present = model.NewBoolVar(f'p_{i}_{j}')
            model.Add(bay[i] == j).OnlyEnforceIf(present)
            model.Add(bay[i] != j).OnlyEnforceIf(present.Not())
            iv = model.NewOptionalIntervalVar(
                start[i], P_list[i], end[i], present, f'iv_{i}_{j}')
            ivs_j.append(iv)
            dems_j.append(min_w[i])
        model.AddCumulative(ivs_j, dems_j, bw_j)

    # 목적함수: Z1 최소화
    model.Minimize(sum(w1 * tard[i] for i in range(n)))

    # warmstart 힌트
    if warmstart:
        for i, ws in warmstart.items():
            model.AddHint(bay[i],   ws["bay_id"])
            model.AddHint(start[i], int(ws["entry_time"]))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timelimit
    solver.parameters.num_workers         = 4
    solver.parameters.log_search_progress = False

    print(f"[HH] CP-SAT solving (budget={timelimit:.1f}s) ...")
    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        obj1 = sum(max(0, solver.Value(end[i]) - D_list[i]) for i in range(n))
        print(f"[HH] CP-SAT done: Z1={obj1:.0f}  status={'OPT' if status==cp_model.OPTIMAL else 'FEAS'}")
        result = {}
        for i in range(n):
            result[i] = {
                "bay_id":     solver.Value(bay[i]),
                "entry_time": solver.Value(start[i]),
                "exit_time":  solver.Value(start[i]) + P_list[i]
            }
        return result
    else:
        print(f"[HH] CP-SAT failed → warmstart 사용")
        return warmstart



    """
    Phase 1.5: 공간 밀도 제약 반영 스케줄 조정 (Slack 기반).

    동시 점유 블록들의 min_w 합이 bay_w 초과 시,
    그 중 slack(due_date - exit_time)이 가장 큰 블록을 뒤로 밀어 T 증가 최소화.
    slack이 큰 블록 = due_date까지 여유가 있는 블록 → 밀어도 tardiness 영향 최소.
    """
    min_w = {}
    for bi in sched:
        bay_id = sched[bi]["bay_id"]
        bw_bay = bays_data[bay_id]["width"]
        bh_bay = bays_data[bay_id]["height"]
        valid_ws = [
            _block_bbox(blocks_data[bi], oi)[2] - _block_bbox(blocks_data[bi], oi)[0]
            for oi in range(len(blocks_data[bi]["shape"]))
            if (_block_bbox(blocks_data[bi], oi)[2] - _block_bbox(blocks_data[bi], oi)[0] <= bw_bay + 1e-6
                and _block_bbox(blocks_data[bi], oi)[3] - _block_bbox(blocks_data[bi], oi)[1] <= bh_bay + 1e-6)
        ]
        min_w[bi] = min(valid_ws) if valid_ws else bw_bay

    adjusted = {bi: dict(a) for bi, a in sched.items()}

    for bay_id in range(n_bays):
        bay_w    = bays_data[bay_id]["width"]
        bay_bids = [bi for bi in adjusted if adjusted[bi]["bay_id"] == bay_id]

        for _ in range(len(bay_bids) * 2):
            changed = False
            for bi in sorted(bay_bids, key=lambda b: adjusted[b]["entry_time"]):
                entry_i = adjusted[bi]["entry_time"]
                exit_i  = adjusted[bi]["exit_time"]
                concurrent = [
                    bj for bj in bay_bids if bj != bi
                    and adjusted[bj]["entry_time"] < exit_i
                    and adjusted[bj]["exit_time"]  > entry_i
                ]
                total_w = min_w[bi] + sum(min_w[bj] for bj in concurrent)
                if total_w <= bay_w + 1e-6:
                    continue
                # slack 가장 큰 블록을 뒤로 밀기 (T 증가 최소화)
                all_group = [bi] + concurrent
                victim = max(all_group,
                             key=lambda b: blocks_data[b]["due_date"] - adjusted[b]["exit_time"])
                others = [b for b in all_group if b != victim]
                if not others:
                    continue
                earliest_other_exit = min(adjusted[b]["exit_time"] for b in others)
                v_proc    = adjusted[victim]["exit_time"] - adjusted[victim]["entry_time"]
                v_release = blocks_data[victim]["release_time"]
                new_entry = max(earliest_other_exit, v_release)
                new_exit  = new_entry + v_proc
                if new_entry != adjusted[victim]["entry_time"]:
                    adjusted[victim]["entry_time"] = int(new_entry)
                    adjusted[victim]["exit_time"]  = int(new_exit)
                    changed = True
            if not changed:
                break

    return adjusted

def _find_x_slot(bi, j, entry_time, exit_time, placed, blocks_data, bays_data):
    """
    Fast path: x 방향 AABB strict non-overlap → check_entry/exit 자동 통과.
    """
    bw = bays_data[j]["width"]
    bh = bays_data[j]["height"]
    block = blocks_data[bi]

    occ = []
    for bk, info in placed.items():
        if info["bay_id"] != j:
            continue
        if info["entry_time"] < exit_time and info["exit_time"] > entry_time:
            occ.append((info["x_min"], info["x_max"]))
    occ.sort()

    n_ori = len(block["shape"])
    for ori_idx in range(n_ori):
        lx0, ly0, lx1, ly1 = _block_bbox(block, ori_idx)
        if lx1 - lx0 > bw + 1e-6 or ly1 - ly0 > bh + 1e-6:
            continue
        px_min = max(0, math.ceil(-lx0))
        candidates = sorted(set(
            [px_min] + [math.ceil(occ_max - lx0) for (_, occ_max) in occ]
        ))
        for px in candidates:
            if px < px_min:
                continue
            if px + lx1 > bw + 1e-6:
                break
            x_min = px + lx0
            x_max = px + lx1
            ok = all(not (x_min < occ_max and occ_min < x_max)
                     for (occ_min, occ_max) in occ)
            if ok:
                py = max(0, math.ceil(-ly0))
                if py + ly1 <= bh + 1e-6:
                    return (int(px), int(py), ori_idx, x_min, x_max)
    return None


def _find_x_slot_slow(bi, j, entry_time, exit_time, placed, blocks_data, bays_data, bays):
    """
    Slow path: check_entry/check_exit 직접 호출 (Shapely 기반).
    AABB로는 겹쳐도 실제 3D 형상으로 통과하는 위치 탐색.
    """
    bay    = bays[j]
    bw     = bays_data[j]["width"]
    bh     = bays_data[j]["height"]
    blkd   = blocks_data[bi]

    # entry 시점에 같은 베이에 있는 블록들
    concurrent = [Block(bk, blocks_data[bk], info["x"], info["y"], info["orient_idx"])
                  for bk, info in placed.items()
                  if info["bay_id"] == j
                  and info["entry_time"] < exit_time
                  and info["exit_time"]  > entry_time]

    # exit 시점에 같은 베이에 있는 블록들
    at_exit = [Block(bk, blocks_data[bk], info["x"], info["y"], info["orient_idx"])
               for bk, info in placed.items()
               if info["bay_id"] == j
               and info["entry_time"] < exit_time]

    n_ori = len(blkd["shape"])
    for ori_idx in range(n_ori):
        lx0, ly0, lx1, ly1 = _block_bbox(blkd, ori_idx)
        if lx1 - lx0 > bw + 1e-6 or ly1 - ly0 > bh + 1e-6:
            continue
        # _candidate_positions으로 후보 생성 (기존 블록 사이 공간 포함)
        cands = _candidate_positions(bw, bh, concurrent, (lx0, ly0, lx1, ly1))
        for px, py in cands:
            new_blk = Block(bi, blkd, px, py, ori_idx)
            if not bay.contains_block(new_blk):
                continue
            if check_entry(bay, concurrent, new_blk, fast=False):
                continue
            if check_exit(bay, at_exit + [new_blk], new_blk, fast=False):
                continue
            x_min = px + lx0
            x_max = px + lx1
            return (int(px), int(py), ori_idx, x_min, x_max)
    return None


def _greedy_schedule(prob_info, timelimit, order=None, bays=None):
    """
    EDD 그리디 + 공간-시간 통합 배치.
    fast path(AABB) 먼저, 실패 시 slow path(Shapely) 시도.
    order를 외부에서 받아 다중 시도 지원.
    """
    t_start     = time.time()
    blocks_data = prob_info["blocks"]
    bays_data   = prob_info["bays"]
    n = len(blocks_data)
    m = len(bays_data)

    if order is None:
        order = sorted(range(n),
                       key=lambda i: (blocks_data[i]["due_date"],
                                      blocks_data[i]["processing_time"]))

    placed = {}

    for bi in order:
        if time.time() - t_start > timelimit * 0.80:
            break

        block = blocks_data[bi]
        R     = block["release_time"]
        D     = block["due_date"]
        P     = int(math.ceil(block["processing_time"]))
        pref  = set(block.get("preference", list(range(m))))

        best       = None
        best_T     = float('inf')
        best_entry = float('inf')
        best_pref  = False

        slack     = max(0, int(D) - int(R) - P)
        max_extra = max(15, slack + 5)

        for entry_time in range(int(R), int(R) + max_extra + 1):
            if time.time() - t_start > timelimit * 0.80:
                break
            exit_time = entry_time + P
            T         = max(0, exit_time - D)
            if best is not None and best_T == 0 and best_pref and T > 0:
                break
            if T > best_T:
                break

            bay_order = sorted(range(m), key=lambda j: (0 if j in pref else 1, j))
            for j in bay_order:
                # fast path
                result = _find_x_slot(bi, j, entry_time, exit_time,
                                      placed, blocks_data, bays_data)
                # slow path (fast 실패 & bays 있을 때만)
                if result is None and bays is not None:
                    result = _find_x_slot_slow(bi, j, entry_time, exit_time,
                                               placed, blocks_data, bays_data, bays)
                if result is None:
                    continue
                px, py, ori_idx, x_min, x_max = result
                is_pref = (j in pref)
                better = (best is None or T < best_T or
                          (T == best_T and is_pref and not best_pref) or
                          (T == best_T and is_pref == best_pref and
                           entry_time < best_entry))
                if better:
                    best_T     = T
                    best_entry = entry_time
                    best_pref  = is_pref
                    best = {"bay_id": j, "entry_time": entry_time,
                            "exit_time": exit_time, "x": px, "y": py,
                            "orient_idx": ori_idx,
                            "x_min": x_min, "x_max": x_max}
                break

            if best is not None and best_T == 0 and best_pref:
                break

        if best is not None:
            placed[bi] = best
        else:
            # fallback: 베이가 비는 시간 이후에 배정
            for j in range(m):
                max_exit = int(R)
                for bk, info in placed.items():
                    if info["bay_id"] == j:
                        max_exit = max(max_exit, info["exit_time"])
                et = max_exit
                xt = et + P
                result = _find_x_slot(bi, j, et, xt, placed, blocks_data, bays_data)
                if result:
                    px, py, ori_idx, x_min, x_max = result
                    placed[bi] = {"bay_id": j, "entry_time": et,
                                  "exit_time": xt, "x": px, "y": py,
                                  "orient_idx": ori_idx,
                                  "x_min": x_min, "x_max": x_max}
                    break

    return placed


def _precompute_x_slots(bay_sched, blocks_data, bay_w, bay_h):
    """
    x 슬롯 사전 할당: [entry, exit] 전체 구간에서 x 범위 strict non-overlap 보장.

    AABB pre-filter 조건: b[0] < a[2] (strict) 이 False이면 자동 통과.
    즉 new_x_min >= exist_x_max → AABB 비겹침 → check_entry/check_exit 자동 통과.

    Returns: {bi: (px, py, oi)}  실패 시 {bi: None}
    """
    result    = {}
    allocated = {}  # bi -> (x_min, x_max, entry, exit)  실제 좌표

    sorted_bids = sorted(bay_sched.keys(),
                         key=lambda b: bay_sched[b]["entry_time"])

    for bi in sorted_bids:
        entry_i  = bay_sched[bi]["entry_time"]
        exit_i   = bay_sched[bi]["exit_time"]
        blk_data = blocks_data[bi]

        # 시간 겹치는 이미 할당된 블록들의 x 범위
        occupied = sorted(
            (xmin, xmax)
            for _, (xmin, xmax, oe, oex) in allocated.items()
            if entry_i < oex and exit_i > oe
        )

        placed = False
        # orientation: x 폭 오름차순 (좁을수록 공간 절약)
        orient_order = sorted(
            range(len(blk_data["shape"])),
            key=lambda o: _block_bbox(blk_data, o)[2] - _block_bbox(blk_data, o)[0]
        )

        for oi in orient_order:
            lx0, ly0, lx1, ly1 = _block_bbox(blk_data, oi)
            bw = lx1 - lx0
            bh = ly1 - ly0
            if bw > bay_w + 1e-6 or bh > bay_h + 1e-6:
                continue

            # y 좌표: bay 바닥에 붙이기
            py = max(0, math.ceil(-ly0))
            if py + ly1 > bay_h + 1e-6:
                continue  # 정수 좌표로 y 방향 배치 불가

            # x 빈 공간 탐색 (strict non-overlap)
            cursor  = 0.0
            x_slot  = None
            for (ox0, ox1) in occupied:
                if ox0 - cursor >= bw - 1e-6:
                    x_slot = cursor
                    break
                cursor = max(cursor, ox1)
            if x_slot is None:
                if cursor + bw <= bay_w + 1e-6:
                    x_slot = cursor
                else:
                    continue

            # px: 정수 좌표, 실제 x_min = px + lx0 >= x_slot 보장
            px = max(0, math.ceil(x_slot - lx0))
            actual_xmin = px + lx0
            actual_xmax = px + lx1
            if actual_xmax > bay_w + 1e-6 or actual_xmin < -1e-6:
                continue

            allocated[bi] = (actual_xmin, actual_xmax, entry_i, exit_i)
            result[bi]    = (px, py, oi)
            placed = True
            break

        if not placed:
            result[bi] = None

    return result



def _spatial_placement(sched, blocks_data, bays, bays_data,
                       t_start, timelimit, per_block_sec=0.3):
    """
    Gurobi 스케줄 (bay_id, entry_time, exit_time) 이 확정된 상태에서
    (x, y, orient_idx) 를 크레인 체크와 함께 결정.
    블록당 per_block_sec 초 초과하면 최소 유효 위치 사용.
    """
    n_bays = len(bays)
    pos = {}

    for bay_id in range(n_bays):
        bay   = bays[bay_id]
        bay_w = bays_data[bay_id]["width"]
        bay_h = bays_data[bay_id]["height"]

        ids = sorted(
            (bi for bi, s in sched.items() if s["bay_id"] == bay_id),
            key=lambda b: sched[b]["entry_time"]
        )

        placed_blks  = []
        placed_sched = []
        slow_ids     = []

        # Fast Path: density violation 해소된 스케줄 → x 슬롯 할당 성공 확률↑
        bay_sched_sub = {bi: sched[bi] for bi in ids}
        x_slots = _precompute_x_slots(bay_sched_sub, blocks_data, bay_w, bay_h)

        for bi in ids:
            pxy = x_slots.get(bi)
            if pxy is not None:
                px, py, oi = pxy
                new_blk = Block(block_id=bi, block_data=blocks_data[bi],
                                x=px, y=py, orient_idx=oi)
                if bay.contains_block(new_blk):
                    pos[bi] = (px, py, oi)
                    placed_blks.append(new_blk)
                    placed_sched.append((sched[bi]["entry_time"], sched[bi]["exit_time"]))
                    continue
            slow_ids.append(bi)

        for bi in slow_ids:
            s_bi    = sched[bi]
            entry_i = s_bi["entry_time"]
            exit_i  = s_bi["exit_time"]
            proc_i  = exit_i - entry_i
            blk_data = blocks_data[bi]
            n_orient = len(blk_data["shape"])

            block_dl = time.time() + per_block_sec
            placed   = False

            for oi in range(n_orient):
                if time.time() > block_dl:
                    break
                lx0, ly0, lx1, ly1 = _block_bbox(blk_data, oi)
                bw, bh = lx1-lx0, ly1-ly0
                if bw > bay_w + 1e-6 or bh > bay_h + 1e-6:
                    continue

                concurrent = [
                    blk for blk, (a, e) in zip(placed_blks, placed_sched)
                    if _time_overlaps(entry_i, exit_i, a, e)
                ]
                candidates = _candidate_positions(bay_w, bay_h, concurrent,
                                                  (lx0, ly0, lx1, ly1))

                for (cx, cy) in candidates:
                    if time.time() > block_dl:
                        break
                    new_blk = Block(block_id=bi, block_data=blk_data,
                                   x=cx, y=cy, orient_idx=oi)
                    if not bay.contains_block(new_blk):
                        continue

                    # Stage-2: 크레인 진입
                    pe = [blk for blk, (a, e) in zip(placed_blks, placed_sched)
                          if a <= entry_i < e]
                    if check_entry(bay, pe, new_blk, fast=True):
                        continue

                    # Stage-3: 크레인 출입
                    px2 = [new_blk] + [blk for blk, (a, e) in zip(placed_blks, placed_sched)
                                       if a < exit_i < e]
                    if check_exit(bay, px2, new_blk, fast=True):
                        continue

                    # Stage-4: 내부 충돌
                    s4 = False
                    for bo, (ao, eo) in zip(placed_blks, placed_sched):
                        if ao <= entry_i or eo >= exit_i:
                            continue
                        if not _time_overlaps(entry_i, exit_i, ao, eo):
                            continue
                        if check_collisions(bay, [new_blk, bo]):
                            s4 = True
                            break
                    if s4:
                        continue

                    pos[bi] = (cx, cy, oi)
                    placed_blks.append(new_blk)
                    placed_sched.append((entry_i, exit_i))
                    placed = True
                    break
                if placed:
                    break

            if not placed:
                # 시간 초과 또는 위치 못 찾음 → bay 안에 들어가는 최소 유효 위치
                fb_placed = False
                for oi in range(n_orient):
                    lx0, ly0, lx1, ly1 = _block_bbox(blk_data, oi)
                    if lx1-lx0 > bay_w+1e-6 or ly1-ly0 > bay_h+1e-6:
                        continue
                    px = max(0, math.ceil(-lx0))
                    py = max(0, math.ceil(-ly0))
                    fb_blk = Block(block_id=bi, block_data=blk_data,
                                   x=px, y=py, orient_idx=oi)
                    if bay.contains_block(fb_blk):
                        pos[bi] = (px, py, oi)
                        placed_blks.append(fb_blk)
                        placed_sched.append((entry_i, exit_i))
                        fb_placed = True
                        break
                if not fb_placed:
                    # bay 자체가 너무 작음 → 일단 넣고 repair에서 다른 bay로 이동
                    pos[bi] = (0, 0, 0)
                    fb_blk = Block(block_id=bi, block_data=blk_data,
                                   x=0, y=0, orient_idx=0)
                    placed_blks.append(fb_blk)
                    placed_sched.append((entry_i, exit_i))

    return pos


# ─────────────────────────────────────────────────────────────────────────────
# Phase 3: 크레인 위반 repair
# ─────────────────────────────────────────────────────────────────────────────

def _try_reposition(bid, assignments, blocks_data, bays, bays_data, n_bays,
                    deadline):
    """
    위반 블록의 시간(entry/exit)은 유지하고 위치(x,y,orient)만 바꿔서
    크레인 통과 가능한 위치 탐색.
    성공 시 True + 수정된 assignments 반환, 실패 시 False.
    """
    a      = assignments[bid]
    bay_id = a["bay_id"]
    entry  = a["entry_time"]
    exit_t = a["exit_time"]
    bay    = bays[bay_id]
    bay_w  = bays_data[bay_id]["width"]
    bay_h  = bays_data[bay_id]["height"]
    blk_data = blocks_data[bid]

    # 같은 베이의 다른 블록들 (최신 assignments 기준)
    others      = [(bi, assignments[bi]) for bi in assignments
                   if bi != bid and assignments[bi]["bay_id"] == bay_id]
    other_blks  = [Block(bi, blocks_data[bi], oa["x"], oa["y"], oa["orient_idx"])
                   for bi, oa in others]
    other_sched = [(oa["entry_time"], oa["exit_time"]) for _, oa in others]

    present_entry = [blk for blk, (a2, e2) in zip(other_blks, other_sched)
                     if a2 <= entry < e2]
    present_exit  = [blk for blk, (a2, e2) in zip(other_blks, other_sched)
                     if a2 < exit_t < e2]

    for oi in range(len(blk_data["shape"])):
        if time.time() > deadline:
            break
        lx0, ly0, lx1, ly1 = _block_bbox(blk_data, oi)
        if lx1-lx0 > bay_w+1e-6 or ly1-ly0 > bay_h+1e-6:
            continue
        candidates = _candidate_positions(bay_w, bay_h, present_entry,
                                          (lx0, ly0, lx1, ly1))
        for (cx, cy) in candidates:
            if time.time() > deadline:
                break
            new_blk = Block(block_id=bid, block_data=blk_data,
                            x=cx, y=cy, orient_idx=oi)
            if not bay.contains_block(new_blk):
                continue
            if check_entry(bay, present_entry, new_blk, fast=True):
                continue
            if check_exit(bay, [new_blk] + present_exit, new_blk, fast=True):
                continue
            # 성공: 위치만 바꿔서 해결
            assignments[bid] = dict(a, x=cx, y=cy, orient_idx=oi)
            return True
    return False


def _repair(prob_info, sol, assignments, blocks_data, bays, bays_data, n_bays,
            t_start, timelimit, max_passes=15):
    """
    위반 블록 repair 전략 (우선순위 순):
      1. 위치 변경만으로 해결 → T 변화 없음 (최선)
      2. 빈 베이 윈도우로 이동 → T 증가하지만 feasibility 보장 (최후 수단)

    bay_schedule을 블록마다 즉시 업데이트해서 중복 윈도우 배정 방지.
    """
    for pass_idx in range(max_passes):
        if time.time() - t_start > timelimit * 0.97:
            break
        result = check_feasibility(prob_info, sol)
        if result["feasible"]:
            break
        viols  = result["violations"]
        stage  = result["stage"]
        elapsed = time.time() - t_start
        print(f"[HH] Repair pass {pass_idx+1}: {len(viols)} violations"
              f"  stage={stage}  elapsed={elapsed:.1f}s")

        to_fix = []
        bid_is_boundary = set()  # "exceeds bay boundary" 에러인 블록들
        seen = set()
        for v in viols:
            try:
                bid = int(v.split("block ")[1].split()[0])
                if bid not in seen:
                    seen.add(bid)
                    to_fix.append(bid)
                if "exceeds bay boundary" in v:
                    bid_is_boundary.add(bid)
            except:
                pass
        if not to_fix:
            break

        # bay_schedule: 블록마다 즉시 업데이트 (중복 윈도우 방지)
        bay_schedule = [[] for _ in range(n_bays)]
        for a in assignments.values():
            bay_schedule[a["bay_id"]].append((a["entry_time"], a["exit_time"]))

        to_fix.sort(key=lambda b: (blocks_data[b]["due_date"],
                                   blocks_data[b]["processing_time"]))

        reposition_budget = timelimit * 0.97 - (time.time() - t_start)
        per_block_dl = reposition_budget / max(len(to_fix), 1)

        n_repositioned = 0
        n_windowed     = 0

        for bid in to_fix:
            if time.time() - t_start > timelimit * 0.97:
                break

            a      = assignments[bid]
            bay_id = a["bay_id"]
            r_time = blocks_data[bid]["release_time"]
            proc   = blocks_data[bid]["processing_time"]

            # ── 전략 1: 위치 변경으로 해결 시도 ──────────────────────────
            deadline = time.time() + min(per_block_dl * 0.8, 3.0)
            if stage in (2, 3) and bid not in bid_is_boundary and \
                    _try_reposition(
                    bid, assignments, blocks_data, bays, bays_data, n_bays,
                    deadline):
                n_repositioned += 1
                continue

            # ── 전략 1.5: bay boundary 에러 → cross-bay 이동 (공간 배치 검증) ──
            if bid in bid_is_boundary:
                moved = False
                deadline_i = blocks_data[bid]["due_date"]
                # T 최소화 순서로 베이 탐색 (현재 베이 제외)
                other_bays = sorted(
                    [j for j in range(n_bays) if j != bay_id],
                    key=lambda j: max(0.0,
                        _empty_bay_entry(bay_schedule[j], r_time, proc)
                        + proc - deadline_i)
                )
                for try_j in other_bays:
                    cand = _empty_bay_entry(bay_schedule[try_j], r_time, proc)
                    pxy  = _place_one_block(
                        bid, try_j, cand, cand + proc,
                        assignments, blocks_data, bays, bays_data)
                    if pxy is not None:
                        old = (a["entry_time"], a["exit_time"])
                        if old in bay_schedule[bay_id]:
                            bay_schedule[bay_id].remove(old)
                        assignments[bid] = dict(a,
                            bay_id=try_j,
                            entry_time=int(cand),
                            exit_time=int(cand + proc),
                            x=int(pxy[0]), y=int(pxy[1]),
                            orient_idx=int(pxy[2]))
                        bay_schedule[try_j].append((cand, cand + proc))
                        n_repositioned += 1
                        moved = True
                        break
                if moved:
                    continue

            # ── 전략 2: 같은 베이 빈 윈도우로 이동 (안전, T는 올라갈 수 있음) ──
            old = (a["entry_time"], a["exit_time"])
            if old in bay_schedule[bay_id]:
                bay_schedule[bay_id].remove(old)

            entry = _empty_bay_entry(bay_schedule[bay_id], r_time, proc)
            x, y  = (0, 0) if stage == 4 else (a["x"], a["y"])
            assignments[bid] = dict(a, x=int(x), y=int(y),
                                    entry_time=int(entry),
                                    exit_time=int(entry + proc))
            # ★ 즉시 업데이트
            bay_schedule[bay_id].append((entry, entry + proc))
            n_windowed += 1

        print(f"[HH]   → reposition={n_repositioned}  window={n_windowed}")
        sol = {"operations": _build_operations(list(assignments.values()))}

    result  = check_feasibility(prob_info, sol)
    status  = "FEASIBLE" if result["feasible"] else f"INFEASIBLE stage={result['stage']}"
    obj_str = f"obj={result['objective']:.0f}" if result["feasible"] else ""
    print(f"[HH] Repair done: {status}  {obj_str}  elapsed={time.time()-t_start:.1f}s")
    return assignments, sol


def _place_one_block(bid, bay_j, entry_i, exit_i,
                     assignments, blocks_data, bays, bays_data):
    """
    블록 하나를 지정된 베이(bay_j)에 공간 배치 시도.
    crane check 없이 bay.contains_block()만 검증 (빠른 버전).
    성공 시 (x, y, orient_idx) 반환, 실패 시 None.
    """
    bay   = bays[bay_j]
    bay_w = bays_data[bay_j]["width"]
    bay_h = bays_data[bay_j]["height"]
    blk_data = blocks_data[bid]
    n_orient = len(blk_data["shape"])

    # 같은 베이의 다른 블록 중 시간 겹치는 것들
    concurrent = []
    for bi, a in assignments.items():
        if bi != bid and a["bay_id"] == bay_j:
            if _time_overlaps(entry_i, exit_i, a["entry_time"], a["exit_time"]):
                concurrent.append(Block(bi, blocks_data[bi], a["x"], a["y"], a["orient_idx"]))

    for oi in range(n_orient):
        lx0, ly0, lx1, ly1 = _block_bbox(blk_data, oi)
        if lx1-lx0 > bay_w+1e-6 or ly1-ly0 > bay_h+1e-6:
            continue
        candidates = _candidate_positions(bay_w, bay_h, concurrent,
                                          (lx0, ly0, lx1, ly1))
        for cx, cy in candidates:
            new_blk = Block(bid, blk_data, cx, cy, oi)
            if bay.contains_block(new_blk):
                return (cx, cy, oi)
    return None


def _improve_phase(prob_info, sol, assignments, blocks_data, bays, bays_data,
                   n_bays, t_start, timelimit):
    """
    Phase 4: feasible 해의 T를 줄이는 post-improvement.
    T > 0 블록들에 대해 다른 베이로 cross-bay 이동 시도.
    공간 배치 검증(_place_one_block) 포함 → infeasible 위험 없음.
    """
    result_cur = check_feasibility(prob_info, sol)
    if not result_cur["feasible"]:
        return assignments, sol

    best_obj  = result_cur["objective"]
    best_sol  = sol
    best_asgn = {k: dict(v) for k, v in assignments.items()}

    for round_i in range(30):
        if time.time() - t_start > timelimit * 0.95:
            break

        tard_bids = sorted(
            [bid for bid, a in assignments.items()
             if a["exit_time"] > blocks_data[bid]["due_date"]],
            key=lambda b: assignments[b]["exit_time"] - blocks_data[b]["due_date"],
            reverse=True
        )
        if not tard_bids:
            break

        asgn_snap = {k: dict(v) for k, v in assignments.items()}
        changed   = False

        for bid in tard_bids[:100]:
            if time.time() - t_start > timelimit * 0.95:
                break

            a          = assignments[bid]
            cur_bay    = a["bay_id"]
            r_time     = blocks_data[bid]["release_time"]
            proc       = blocks_data[bid]["processing_time"]
            deadline_i = blocks_data[bid]["due_date"]
            cur_tard   = max(0, a["exit_time"] - deadline_i)

            best_j, best_e, best_pos = cur_bay, None, None
            best_new_tard = cur_tard  # 현재보다 줄어야만 이동

            for try_j in range(n_bays):
                # 이 베이에서 빈 윈도우 entry 계산
                sched_j = [(assignments[bi2]["entry_time"],
                            assignments[bi2]["exit_time"])
                           for bi2 in assignments
                           if bi2 != bid and assignments[bi2]["bay_id"] == try_j]
                cand     = _empty_bay_entry(sched_j, r_time, proc)
                new_tard = max(0.0, cand + proc - deadline_i)

                if new_tard < best_new_tard:
                    # 공간 배치 가능한지 확인
                    pxy = _place_one_block(bid, try_j, cand, cand + proc,
                                           assignments, blocks_data, bays, bays_data)
                    if pxy is not None:
                        best_new_tard = new_tard
                        best_j  = try_j
                        best_e  = cand
                        best_pos = pxy

            if best_e is not None:
                assignments[bid] = dict(a,
                    bay_id=best_j,
                    entry_time=int(best_e),
                    exit_time=int(best_e + proc),
                    x=int(best_pos[0]),
                    y=int(best_pos[1]),
                    orient_idx=int(best_pos[2]))
                changed = True

        if not changed:
            break

        # repair로 혹시 생긴 crane 위반 처리
        sol_try = {"operations": _build_operations(list(assignments.values()))}
        assignments, sol_try = _repair(
            prob_info, sol_try, assignments, blocks_data,
            bays, bays_data, n_bays, t_start,
            timelimit * 0.95, max_passes=8)

        result_try = check_feasibility(prob_info, sol_try)
        if result_try["feasible"] and result_try["objective"] < best_obj:
            best_obj  = result_try["objective"]
            best_sol  = sol_try
            best_asgn = {k: dict(v) for k, v in assignments.items()}
            print(f"[HH] Improve round {round_i+1}: "
                  f"obj={best_obj:.0f}  Z1={result_try['obj1']:.0f}"
                  f"  elapsed={time.time()-t_start:.1f}s")
        else:
            # 개선 없으면 rollback
            assignments = asgn_snap
            break

    return best_asgn, best_sol


# ─────────────────────────────────────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────────────────────────────────────

def hhalgorithm(prob_info, timelimit=60):
    t_start = time.time()

    bays_data   = prob_info["bays"]
    blocks_data = prob_info["blocks"]
    n_bays      = len(bays_data)
    n_blocks    = len(blocks_data)
    w1 = prob_info.get("weights", {}).get("w1", 1.0)
    w2 = prob_info.get("weights", {}).get("w2", 1.0)
    w3 = prob_info.get("weights", {}).get("w3", 1.0)

    print(f"[HH] Instance : {prob_info.get('name','?')}")
    print(f"[HH] Bays : {n_bays}  Blocks : {n_blocks}  Timelimit : {timelimit:.1f}s")
    print(f"[HH] Weights : w1={w1}  w2={w2}  w3={w3}")

    bays = [Bay.from_dict(d, i) for i, d in enumerate(bays_data)]
    for i, b in enumerate(bays):
        print(f"[HH]   bay[{i}]  {b.width}x{b.height}")

    # ── Phase 0: EDD warmstart ─────────────────────────────────────────────
    print(f"[HH] Phase 0: EDD warmstart ...")
    warmstart = _edd_warmstart(prob_info)
    print(f"[HH] Phase 0 done  t={time.time()-t_start:.2f}s")

    # ── Phase 1: 그리디로 초기해 → CP-SAT으로 개선 ───────────────────────
    print(f"[HH] Phase 1: Greedy warmstart ...")
    greedy_order = sorted(range(n_blocks),
                          key=lambda i: (blocks_data[i]["due_date"],
                                         blocks_data[i]["processing_time"]))
    placed_greedy = _greedy_schedule(prob_info, timelimit,
                                     order=greedy_order, bays=bays)
    warmstart_ws  = {bi: {"bay_id":     info["bay_id"],
                          "entry_time": info["entry_time"],
                          "exit_time":  info["exit_time"]}
                     for bi, info in placed_greedy.items()}
    for bi in range(n_blocks):
        if bi not in warmstart_ws:
            R = int(blocks_data[bi]["release_time"])
            P = int(math.ceil(blocks_data[bi]["processing_time"]))
            warmstart_ws[bi] = {"bay_id": 0, "entry_time": R, "exit_time": R+P}
    T_greedy = sum(max(0, warmstart_ws[bi]["exit_time"] - blocks_data[bi]["due_date"])
                   for bi in range(n_blocks))
    print(f"[HH] Greedy done  t={time.time()-t_start:.2f}s  T_sum={T_greedy}")

    cpsat_budget = timelimit - (time.time() - t_start) - 8
    sched = _cpsat_schedule(prob_info, warmstart_ws, max(5.0, cpsat_budget))
    print(f"[HH] Phase 1 done  t={time.time()-t_start:.2f}s")

    # ── Phase 2: _precompute_x_slots로 x 위치 결정 ────────────────────────
    print(f"[HH] Phase 2: x-slot placement ...")
    pos = {}
    for j in range(n_bays):
        bay_sched_j = {bi: {"entry_time": sched[bi]["entry_time"],
                            "exit_time":  sched[bi]["exit_time"]}
                       for bi in sched if sched[bi]["bay_id"] == j}
        slots_j = _precompute_x_slots(bay_sched_j, blocks_data,
                                       bays_data[j]["width"], bays_data[j]["height"])
        for bi, slot in slots_j.items():
            if slot is not None:
                pos[bi] = slot

    assignments = {}
    for bi, s in sched.items():
        px, py, oi = pos.get(bi, (0, 0, 0))
        assignments[bi] = {
            "block_id":   bi,
            "bay_id":     s["bay_id"],
            "entry_time": s["entry_time"],
            "exit_time":  s["exit_time"],
            "x": int(px), "y": int(py), "orient_idx": oi
        }
    for bi in range(n_blocks):
        if bi not in assignments:
            R = int(blocks_data[bi]["release_time"])
            P = int(math.ceil(blocks_data[bi]["processing_time"]))
            assignments[bi] = {
                "block_id": bi, "bay_id": 0,
                "entry_time": R, "exit_time": R+P,
                "x": 0, "y": 0, "orient_idx": 0
            }
    print(f"[HH] Phase 2 done  t={time.time()-t_start:.2f}s")

    # ── Phase 3: Repair ────────────────────────────────────────────────────
    print(f"[HH] Phase 3: repair ...")
    sol = {"operations": _build_operations(list(assignments.values()))}
    assignments, sol = _repair(prob_info, sol, assignments, blocks_data,
                               bays, bays_data, n_bays, t_start,
                               timelimit * 0.55)

    # ── Phase 4: T 개선 (남은 시간 활용, 공간 배치 검증 포함) ─────────────
    result_p3 = check_feasibility(prob_info, sol)
    if result_p3["feasible"]:
        print(f"[HH] Phase 4: T improvement ...")
        assignments, sol = _improve_phase(
            prob_info, sol, assignments, blocks_data,
            bays, bays_data, n_bays, t_start, timelimit)

    # ── 최종 결과 ──────────────────────────────────────────────────────────
    final = check_feasibility(prob_info, sol)
    elapsed = time.time() - t_start
    print(f"[HH] Done | {n_blocks}/{n_blocks}  elapsed={elapsed:.2f}s")
    if final["feasible"]:
        print(f"[HH] FEASIBLE  obj={final['objective']:.0f}"
              f"  Z1={final['obj1']:.1f}"
              f"  Z2={final['obj2']:.1f}"
              f"  Z3={final['obj3']:.1f}")
    else:
        print(f"[HH] INFEASIBLE stage={final['stage']}"
              f"  violations={len(final['violations'])}")
        for v in final["violations"][:3]:
            print(f"[HH]   {v}")
    return sol
