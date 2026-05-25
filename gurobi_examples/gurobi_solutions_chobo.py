#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║       Python + Gurobi 초급 예제 — 정답지                       ║
╚══════════════════════════════════════════════════════════════╝
"""

import numpy as np
import gurobipy as gp
from gurobipy import GRB


# ══════════════════════════════════════════════════════════════
# 문제 1  ★☆☆  LP 기초 — 생산량 결정
# ══════════════════════════════════════════════════════════════
# 핵심 개념: addVar, addConstr, setObjective, optimize, .X
print("=" * 55)
print("문제 1 — LP 기초 (생산량 결정)")
print("=" * 55)

with gp.Model("p1_production") as m:
    m.setParam("OutputFlag", 0)     # 로그 출력 끄기

    # 결정변수: 연속형(기본값), lb=0
    x_A = m.addVar(name="x_A")
    x_B = m.addVar(name="x_B")

    # 제약 조건
    m.addConstr(3*x_A + 2*x_B <= 120, name="machine")
    m.addConstr(  x_A + 2*x_B <= 80,  name="labor")

    # 목적 함수: 최대화
    m.setObjective(5*x_A + 4*x_B, GRB.MAXIMIZE)

    m.optimize()

    print(f"  최적 생산량  x_A = {x_A.X:.1f} 개")
    print(f"  최적 생산량  x_B = {x_B.X:.1f} 개")
    print(f"  최대 이익       = {m.ObjVal:.1f} 원")
    # 예상 정답: x_A=20, x_B=30, ObjVal=220
    print()

    # ── 학습 포인트 ───────────────────────────────────────────
    # m.addVar()       : 변수 추가 (기본: 연속형, lb=0, ub=GRB.INFINITY)
    # m.addConstr()    : 선형 제약 추가
    # m.setObjective() : 목적함수 설정 (GRB.MAXIMIZE / GRB.MINIMIZE)
    # m.optimize()     : 최적화 실행
    # var.X            : 최적해에서의 변수값


# ══════════════════════════════════════════════════════════════
# 문제 2  ★☆☆  ILP — 배낭 문제
# ══════════════════════════════════════════════════════════════
# 핵심 개념: vtype=GRB.BINARY, quicksum
print("=" * 55)
print("문제 2 — 배낭 문제 (Binary ILP)")
print("=" * 55)

weights  = [2, 3, 4, 5, 9]
values   = [3, 4, 5, 8, 10]
capacity = 10
n_items  = len(weights)

with gp.Model("p2_knapsack") as m:
    m.setParam("OutputFlag", 0)

    # 이진 변수: 물건을 담으면 1, 안 담으면 0
    x = m.addVars(n_items, vtype=GRB.BINARY, name="x")

    # 무게 제약
    m.addConstr(
        gp.quicksum(weights[i] * x[i] for i in range(n_items)) <= capacity,
        name="weight"
    )

    # 목적함수: 가치 최대화
    m.setObjective(
        gp.quicksum(values[i] * x[i] for i in range(n_items)),
        GRB.MAXIMIZE
    )

    m.optimize()

    selected = [i for i in range(n_items) if x[i].X > 0.5]
    total_w  = sum(weights[i] for i in selected)
    print(f"  선택된 물건: {selected}")
    print(f"  총 무게    : {total_w}")
    print(f"  총 가치    : {m.ObjVal:.0f}")
    # 예상 정답: 물건 [1,2,3] 선택, 무게=12→ 아님
    # 실제 정답: 물건 [0,1,3] 무게=10, 가치=15
    print()

    # ── 학습 포인트 ───────────────────────────────────────────
    # m.addVars(n, ...)    : n개 변수를 딕셔너리로 한번에 추가
    # vtype=GRB.BINARY     : 0/1 이진 변수
    # gp.quicksum(...)     : sum()보다 빠른 Gurobi 전용 합산 함수
    # x[i].X > 0.5         : 이진 변수 최적값 읽기 (부동소수 오차 처리)


# ══════════════════════════════════════════════════════════════
# 문제 3  ★★☆  MVar — 운송 문제
# ══════════════════════════════════════════════════════════════
# 핵심 개념: addMVar, axis 합계, 행렬 목적함수
print("=" * 55)
print("문제 3 — 운송 문제 (MVar 행렬 변수)")
print("=" * 55)

supply = np.array([30, 40])
demand = np.array([20, 25, 25])
cost   = np.array([[2, 3, 1],
                   [5, 4, 8]])

with gp.Model("p3_transport") as m:
    m.setParam("OutputFlag", 0)

    # 2×3 연속형 행렬 변수 (기본 lb=0)
    x = m.addMVar((2, 3), name="x")

    # 공급 제약: 각 행의 합 ≤ supply
    m.addConstr(x.sum(axis=1) <= supply, name="supply")

    # 수요 제약: 각 열의 합 ≥ demand
    m.addConstr(x.sum(axis=0) >= demand, name="demand")

    # 목적함수: 원소별 곱 후 합산
    m.setObjective((cost * x).sum(), GRB.MINIMIZE)

    m.optimize()

    print("  최적 운송량 행렬:")
    print(np.round(x.X, 1))
    print(f"  최소 총 운송비 = {m.ObjVal:.1f}")
    # 예상 정답: ObjVal = 130
    print()

    # ── 학습 포인트 ───────────────────────────────────────────
    # m.addMVar((m,n), ...)     : m×n 행렬 변수 (NumPy 연산 호환)
    # x.sum(axis=1)             : 행별 합계 → shape (m,)
    # x.sum(axis=0)             : 열별 합계 → shape (n,)
    # (cost * x).sum()          : 원소별 곱의 전체 합 = 내적(dot product)
    # addConstr(배열)            : 벡터/행렬 제약을 한 줄로 추가


# ══════════════════════════════════════════════════════════════
# 문제 4  ★★☆  이진 변수 + 빅-M — 설비 입지 선정
# ══════════════════════════════════════════════════════════════
# 핵심 개념: 두 종류 이진변수 연동, addVars 2차원
print("=" * 55)
print("문제 4 — 설비 입지 선정 (Big-M 제약)")
print("=" * 55)

fixed_cost   = [10, 20, 15]
service_cost = np.array([[3, 5, 4],
                         [2, 1, 6],
                         [7, 3, 2],
                         [4, 6, 3],
                         [5, 2, 8]])
I, J = service_cost.shape  # I=5 고객, J=3 창고

with gp.Model("p4_facility") as m:
    m.setParam("OutputFlag", 0)

    # y[j] = 1: 창고 j 오픈
    y = m.addVars(J, vtype=GRB.BINARY, name="y")
    # x[i,j] = 1: 고객 i → 창고 j 배정
    x = m.addVars(I, J, vtype=GRB.BINARY, name="x")

    # 각 고객은 정확히 1개 창고에 배정
    for i in range(I):
        m.addConstr(gp.quicksum(x[i, j] for j in range(J)) == 1,
                    name=f"assign_{i}")

    # 빅-M 제약: 창고 j가 열려야 고객 배정 가능
    for i in range(I):
        for j in range(J):
            m.addConstr(x[i, j] <= y[j], name=f"link_{i}_{j}")

    # 최대 2개 창고 오픈
    m.addConstr(gp.quicksum(y[j] for j in range(J)) <= 2, name="max_open")

    # 목적함수: 고정비 + 서비스비
    obj = (gp.quicksum(fixed_cost[j] * y[j] for j in range(J)) +
           gp.quicksum(service_cost[i, j] * x[i, j]
                       for i in range(I) for j in range(J)))
    m.setObjective(obj, GRB.MINIMIZE)

    m.optimize()

    opened = [j for j in range(J) if y[j].X > 0.5]
    print(f"  오픈 창고: {opened}")
    for i in range(I):
        assigned = [j for j in range(J) if x[i, j].X > 0.5][0]
        print(f"  고객 {i} → 창고 {assigned}")
    print(f"  최소 총 비용 = {m.ObjVal:.0f}")
    print()

    # ── 학습 포인트 ───────────────────────────────────────────
    # x[i,j] <= y[j]           : 빅-M 제약의 핵심 패턴
    #                             "창고 안 열면(y=0) 배정 불가(x=0)"
    # gp.quicksum(... for ...)  : 2중 반복 합산
    # 두 종류 변수 목적함수 합산  : 고정비(y) + 변동비(x) 동시 최적화


# ══════════════════════════════════════════════════════════════
# 문제 5  ★★★  MVar 이진 행렬 — 작업 배정
# ══════════════════════════════════════════════════════════════
# 핵심 개념: MVar + BINARY, 행/열 합계 == 1 (등호 제약)
print("=" * 55)
print("문제 5 — 작업 배정 (Assignment Problem)")
print("=" * 55)

cost_matrix = np.array([[9, 2, 7, 8],
                        [6, 4, 3, 7],
                        [5, 8, 1, 8],
                        [7, 6, 9, 4]])
N = 4  # 작업자 수 = 작업 수

with gp.Model("p5_assignment") as m:
    m.setParam("OutputFlag", 0)

    # N×N 이진 행렬 변수
    x = m.addMVar((N, N), vtype=GRB.BINARY, name="x")

    # 각 작업자는 정확히 1개 작업
    m.addConstr(x.sum(axis=1) == np.ones(N), name="one_job_per_worker")

    # 각 작업은 정확히 1명의 작업자
    m.addConstr(x.sum(axis=0) == np.ones(N), name="one_worker_per_job")

    # 목적함수: 총 비용 최소화
    m.setObjective((cost_matrix * x).sum(), GRB.MINIMIZE)

    m.optimize()

    print("  최적 배정 행렬 (1 = 배정됨):")
    print(x.X.astype(int))
    print()
    for i in range(N):
        j = np.argmax(x.X[i])
        print(f"  작업자 {i} → 작업 {j}  (비용 {cost_matrix[i, j]})")
    print(f"  최소 총 비용 = {m.ObjVal:.0f}")
    # 예상 정답: 비용 = 13  (0→1, 1→2, 2→0 또는 유사 배정)
    print()

    # ── 학습 포인트 ───────────────────────────────────────────
    # addMVar + BINARY           : 행렬 이진변수 (addVars 2중 루프 대체)
    # x.sum(axis=1) == np.ones() : 행 합계 == 1 벡터 등호 제약
    # np.argmax(x.X[i])          : i번째 행에서 1인 열 인덱스 추출


# ══════════════════════════════════════════════════════════════
# 요약: Gurobi 핵심 API 치트시트
# ══════════════════════════════════════════════════════════════
print("=" * 55)
print("Gurobi 핵심 API 치트시트")
print("=" * 55)
cheatsheet = """
  ┌─────────────────────────────────────────────────────┐
  │ 모델 생성                                              │
  │   m = gp.Model("name")                               │
  │                                                       │
  │ 변수 추가                                              │
  │   m.addVar(lb, ub, vtype, name)   # 스칼라 변수        │
  │   m.addVars(n, vtype, name)       # n개 변수 딕셔너리   │
  │   m.addMVar((m,n), vtype, name)   # m×n 행렬 변수      │
  │                                                       │
  │ vtype 종류                                             │
  │   GRB.CONTINUOUS (기본)  GRB.INTEGER  GRB.BINARY      │
  │                                                       │
  │ 제약 추가                                              │
  │   m.addConstr(expr, name)         # 단일 제약           │
  │   m.addConstrs(gen, name)         # 제약 생성자          │
  │                                                       │
  │ 목적함수                                               │
  │   m.setObjective(expr, GRB.MINIMIZE / GRB.MAXIMIZE)  │
  │                                                       │
  │ 최적화 & 결과                                           │
  │   m.optimize()                                        │
  │   m.ObjVal                        # 최적 목적값         │
  │   var.X                           # 변수 최적값         │
  │   m.Status == GRB.OPTIMAL (==2)   # 최적해 확인         │
  │                                                       │
  │ 유틸리티                                               │
  │   gp.quicksum(...)                # 빠른 합산           │
  │   m.setParam("OutputFlag", 0)     # 로그 끄기           │
  └─────────────────────────────────────────────────────┘
"""
print(cheatsheet)
