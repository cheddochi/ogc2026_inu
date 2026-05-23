#!/usr/bin/env python3
"""
RoRo Ship Stowage Optimization — Gurobi MIP
FAST 2025 Competition (UNIST Robotics & Mobility Lab SA 발표 재현)

══════════════════════════════════════════════════════════════
문제 정의
══════════════════════════════════════════════════════════════
  선박 갑판을 그래프로 모델링.  차량(vehicle)을 노드(parking slot)에
  최적 배치하여 항구별 하역 시 발생하는 임시하역(reshuffling) 횟수를
  최소화한다.

  임시하역이란? 목적 항구에서 차량 k를 내릴 때, k의 출구 경로를
  막고 있는 차량 v를 잠시 다른 곳으로 옮기는 작업.
  ( dest_port[v] > dest_port[k] 인 v가 k보다 출구에 가까이 있을 때 발생 )

══════════════════════════════════════════════════════════════
MIP 정식화
══════════════════════════════════════════════════════════════
  결정변수
    x[v,n]   ∈ {0,1}  차량 v를 노드 n에 배치하면 1
    blk[v,k] ∈ {0,1}  차량 v가 차량 k의 출구 경로를 막으면 1

  목적함수
    min  Σ_(v,k) blk[v,k]

  제약조건
    (C1) Σ_n  x[v,n] = 1         ∀v      차량당 정확히 1 슬롯
    (C2) Σ_v  x[v,n] ≤ 1         ∀n      슬롯당 최대 1대
    (C3) blk[v,k] ≥ x[v,a] + x[k,b] - 1
         ∀ (v,k) s.t. dest[v]>dest[k],  ∀ (a,b) s.t. a∈path(b→EXIT)
         (블로킹 논리 선형화)
"""

import numpy as np
import gurobipy as gp
from gurobipy import GRB
import networkx as nx

# ═══════════════════════════════════════════════════════════
# 1. 선박 갑판 그래프 (23 노드)
#    Node 0 = 출구 / 경사로(Ramp)
#    슬라이드의 그래프 구조를 최대한 재현
# ═══════════════════════════════════════════════════════════
EXIT_NODE = 0

deck_edges = [
    # 출구 → 갑판 중앙 통로
    (0, 1), (1, 2), (2, 3), (3, 4), (4, 5),
    # 중앙 분기
    (5, 6), (5, 11),
    # 좌측 영역
    (6, 7), (6, 9),
    (7, 8), (8, 11), (8, 12),
    # 좌-후방 영역
    (9, 15), (9, 16),
    (10, 14), (10, 15),
    # 후미 영역
    (11, 17), (12, 13), (12, 18),
    (14, 19), (15, 20), (16, 20),
    (19, 21), (20, 22),
]

G = nx.Graph()
G.add_nodes_from(range(23))
G.add_edges_from(deck_edges)

assert nx.is_connected(G), "갑판 그래프가 연결되지 않음"

# 주차 가능 노드 (Exit 제외), 출구로부터 거리(깊이)
parking = sorted(n for n in G.nodes() if n != EXIT_NODE)
depth   = nx.single_source_shortest_path_length(G, EXIT_NODE)

# ── 블로킹 노드 쌍 전처리 ──
# (a, b): 노드 a가 b→EXIT 최단경로의 중간 노드
#  → 차량이 a에 있으면, b에 있는 차량의 하역을 막음
blocking_node_pairs = []
for b in parking:
    path = nx.shortest_path(G, b, EXIT_NODE)  # b → 0
    for a in path[1:-1]:                      # 중간 노드만 (b·EXIT 제외)
        if a != EXIT_NODE:
            blocking_node_pairs.append((a, b))

print("=" * 60)
print("  RoRo Ship Stowage Optimization — Gurobi MIP")
print("=" * 60)
print(f"  그래프     : {G.number_of_nodes()} 노드,  {G.number_of_edges()} 엣지")
print(f"  주차 슬롯  : {len(parking)} 개")
print(f"  블로킹 노드 쌍 : {len(blocking_node_pairs)} 쌍")


# ═══════════════════════════════════════════════════════════
# 2. 문제 인스턴스  (차량 15대 · 3개 목적 항구)
#
#    항구 번호가 작을수록 먼저 들르는 가까운 항구
#    → 단기화물(항구 1)은 출구 가까이, 장기화물(항구 3)은 깊은 곳에
# ═══════════════════════════════════════════════════════════
dest_port = (
    [1, 1, 1, 1]        +   # 4대 → 항구 1 (단기화물)
    [2, 2, 2, 2, 2]     +   # 5대 → 항구 2
    [3, 3, 3, 3, 3, 3]      # 6대 → 항구 3 (장기화물)
)

V = range(len(dest_port))     # 차량 인덱스
P = sorted(set(dest_port))    # 항구 목록 [1, 2, 3]

# dest[v] > dest[k] 인 쌍만 블로킹 가능
blocking_veh_pairs = [
    (v, k) for v in V for k in V
    if v != k and dest_port[v] > dest_port[k]
]

print(f"\n  차량 수    : {len(dest_port)} 대")
print(f"  항구별 수  : { {p: dest_port.count(p) for p in P} }")
print(f"  블로킹 차량 쌍 : {len(blocking_veh_pairs)} 쌍")
print(f"  C3 제약 수 : {len(blocking_veh_pairs) * len(blocking_node_pairs)}")


# ═══════════════════════════════════════════════════════════
# 3. Gurobi MIP 모델 구성 및 최적화
# ═══════════════════════════════════════════════════════════
with gp.Env() as env, gp.Model("RoRo_Stowage", env=env) as m:

    # ── 결정변수 ──────────────────────────────────────────
    # x[v,n] = 1  :  차량 v → 노드 n 배치
    x = m.addVars(
        [(v, n) for v in V for n in parking],
        vtype=GRB.BINARY, name="x"
    )

    # blk[v,k] = 1  :  차량 v가 차량 k의 출구경로를 차단
    blk = m.addVars(
        blocking_veh_pairs, vtype=GRB.BINARY, name="blk"
    )

    # ── 목적함수 ──────────────────────────────────────────
    # 전체 임시하역 횟수 최소화
    m.setObjective(blk.sum(), GRB.MINIMIZE)

    # ── 제약조건 ──────────────────────────────────────────

    # (C1) 차량당 정확히 1개 슬롯
    m.addConstrs(
        (gp.quicksum(x[v, n] for n in parking) == 1 for v in V),
        name="C1_assign"
    )

    # (C2) 슬롯당 최대 1대
    m.addConstrs(
        (gp.quicksum(x[v, n] for v in V) <= 1 for n in parking),
        name="C2_cap"
    )

    # (C3) 블로킹 선형화
    #   차량 v가 노드 a에 있고, 차량 k가 노드 b에 있는데
    #   a가 b→EXIT 경로를 막으면 → blk[v,k] 강제로 1
    for (v, k) in blocking_veh_pairs:
        for (a, b) in blocking_node_pairs:
            m.addConstr(
                blk[v, k] >= x[v, a] + x[k, b] - 1,
                name=f"C3_{v}_{k}_{a}_{b}"
            )

    # ── 솔버 파라미터 ─────────────────────────────────────
    m.setParam("TimeLimit",  180)   # 최대 3분
    m.setParam("MIPGap",     0.01)  # 1% 갭에서 조기 종료
    m.setParam("Threads",    4)     # 병렬 스레드

    m.optimize()


    # ═══════════════════════════════════════════════════════
    # 4. 결과 출력
    # ═══════════════════════════════════════════════════════
    if m.SolCount == 0:
        print("\n해를 찾지 못했습니다.")
    else:
        assign = {
            v: n for v in V for n in parking if x[v, n].X > 0.5
        }

        print("\n" + "=" * 60)
        print(f"  ✅ 목적값 (총 임시하역)  : {m.ObjVal:.0f} 회")
        print(f"  ✅ MIP Gap              : {m.MIPGap:.2%}")
        print(f"  ✅ Status               : {m.Status}")
        print("=" * 60)

        # ── 배치 테이블 ──
        try:
            import pandas as pd

            rows = []
            for v in V:
                n = assign[v]
                # 이 차량이 어떤 차량을 막는지
                blocks_whom = [
                    k + 1 for (u, k) in blocking_veh_pairs
                    if u == v and blk[u, k].X > 0.5
                ]
                rows.append({
                    "차량":      v + 1,
                    "배치노드":  n,
                    "깊이":      depth[n],
                    "목적항구":  dest_port[v],
                    "블로킹 대상": str(blocks_whom) if blocks_whom else "-",
                })

            df = pd.DataFrame(rows).sort_values("목적항구")
            print("\n▶ 차량 배치 결과:")
            print(df.to_string(index=False))

        except ImportError:
            print("\n▶ 차량 배치 결과 (pandas 없음):")
            print(f"{'차량':>4} {'노드':>5} {'깊이':>5} {'항구':>5}")
            for v in sorted(V, key=lambda v: dest_port[v]):
                print(f"{v+1:>4}  {assign[v]:>4}  {depth[assign[v]]:>4}  {dest_port[v]:>4}")

        # ── 항구별 임시하역 횟수 ──
        print("\n▶ 항구별 임시하역 횟수:")
        total = 0
        for p in P:
            c = sum(
                blk[v, k].X
                for (v, k) in blocking_veh_pairs
                if dest_port[k] == p
            )
            print(f"   항구 {p}: {c:.0f} 회")
            total += c
        print(f"   합계  : {total:.0f} 회  (≈ 목적값 {m.ObjVal:.0f})")

        # ── 항구별 평균 깊이 검증 ──
        # 선적 휴리스틱 원칙: 장기화물일수록 깊은 노드에 배치
        print("\n▶ 항구 그룹별 평균 깊이 (클수록 출구에서 멀리 배치됨):")
        for p in P:
            avg = np.mean([depth[assign[v]] for v in V if dest_port[v] == p])
            label = "단기화물" if p == min(P) else ("장기화물" if p == max(P) else "중간")
            print(f"   항구 {p} ({label}): 평균 깊이 {avg:.2f}")

        # ── 이론적 비교: 완전 랜덤 배치 대비 개선율 ──
        print("\n▶ 참고: 랜덤 배치 대비 절감 효과 추정")
        # 랜덤 배치 시 블로킹 기댓값: (차량수/슬롯수) * 블로킹 쌍 수 / 차량 수
        rand_expected = len(blocking_veh_pairs) * len(parking) / (len(parking) ** 2)
        approx_rand   = len(blocking_veh_pairs) * (len(V) / len(parking))
        print(f"   랜덤 배치 추정 임시하역: ~{approx_rand:.0f} 회")
        print(f"   MIP 최적해             : {m.ObjVal:.0f} 회")
        if approx_rand > 0:
            print(f"   절감률 추정            : {(1 - m.ObjVal/approx_rand)*100:.1f}%")