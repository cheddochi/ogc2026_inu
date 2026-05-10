"""
OGC 2025 - 테스트 문제 생성기
샘플 문제를 생성하고 JSON으로 저장합니다.

사용법:
    python problem_generator.py              # 기본 small 문제 생성
    python problem_generator.py --size large # large 문제 생성
"""

import json
import random
import argparse
import numpy as np
from collections import deque


def bfs_distances(edges, N, start=0):
    """BFS로 start 노드에서 모든 노드까지의 최단거리 계산"""
    adj = {i: [] for i in range(N)}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    dist = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for nb in adj[node]:
            if nb not in dist:
                dist[nb] = dist[node] + 1
                queue.append(nb)
    return dist


def compute_lb(N, edges, K, P, F):
    """
    하한값(LB) 계산
    - 각 수요 단위마다 최소 2개 경로(적재 + 하역) 필요
    - 각 경로 비용 = F + (게이트와 가장 가까운 노드까지 거리)
    """
    dist_from_gate = bfs_distances(edges, N, start=0)
    min_dist = min(dist_from_gate[n] for n in range(1, N))  # 게이트 제외

    lb = 0
    for (o, d), qty in K:
        # 적재 경로 + 하역 경로 × 수량
        lb += qty * 2 * (F + min_dist)
    return lb


def make_grid_graph(rows, cols):
    """
    게이트(0)에 연결된 격자 그래프 생성
    노드 레이아웃:
        0(gate) - 1 - 2 - ... - cols
                  |   |         |
                 ...           ...
    """
    # 격자 노드: 1 ~ rows*cols
    N = rows * cols + 1  # 0: gate
    edges = []

    def node_id(r, c):
        return r * cols + c + 1  # 1-based

    # 격자 내부 엣지
    for r in range(rows):
        for c in range(cols):
            n = node_id(r, c)
            if c + 1 < cols:
                edges.append((n, node_id(r, c + 1)))  # 오른쪽
            if r + 1 < rows:
                edges.append((n, node_id(r + 1, c)))  # 아래

    # 게이트(0)를 첫 번째 열의 모든 노드에 연결
    for r in range(rows):
        edges.append((0, node_id(r, 0)))

    return N, edges


def generate_problem(size="small", seed=42):
    random.seed(seed)
    np.random.seed(seed)

    configs = {
        "tiny":  dict(rows=2, cols=3, P=2, F=10, demands_per_pair=1),
        "small": dict(rows=3, cols=4, P=3, F=10, demands_per_pair=2),
        "medium":dict(rows=4, cols=6, P=4, F=10, demands_per_pair=3),
        "large": dict(rows=5, cols=8, P=5, F=10, demands_per_pair=4),
    }
    cfg = configs[size]

    N, edges = make_grid_graph(cfg["rows"], cfg["cols"])
    P = cfg["P"]
    F = cfg["F"]

    # 수요 생성: 모든 (출발항, 도착항) 쌍에 대해 생성
    K = []
    for o in range(P - 1):
        for d in range(o + 1, P):
            qty = random.randint(1, cfg["demands_per_pair"])
            K.append([[o, d], qty])

    LB = compute_lb(N, edges, K, P, F)

    prob_info = {
        "N": N,
        "E": edges,
        "K": K,
        "P": P,
        "F": F,
        "LB": LB
    }

    return prob_info


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OGC2025 테스트 문제 생성기")
    parser.add_argument("--size", choices=["tiny", "small", "medium", "large"],
                        default="small", help="문제 크기 (기본값: small)")
    parser.add_argument("--seed", type=int, default=42, help="랜덤 시드")
    parser.add_argument("--out", type=str, default=None, help="출력 파일명 (기본: problem_{size}.json)")
    args = parser.parse_args()

    prob = generate_problem(size=args.size, seed=args.seed)

    out_file = args.out or f"problem_{args.size}.json"
    with open(out_file, "w") as f:
        json.dump(prob, f, indent=2)

    print(f"✅ 문제 생성 완료: {out_file}")
    print(f"   N={prob['N']}, E={len(prob['E'])}, K={len(prob['K'])}, P={prob['P']}, F={prob['F']}, LB={prob['LB']:.1f}")
    total_qty = sum(qty for (_, qty) in prob['K'])
    print(f"   총 수요량: {total_qty}")
