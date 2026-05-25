# ══════════════════════════════════════════════════════════════
# 문제 3  ★★☆  행렬 변수(MVar) — 운송 문제
# ══════════════════════════════════════════════════════════════
"""
[문제 3] 운송 문제 (Transportation Problem)

  공급지 2곳(S0, S1), 수요지 3곳(D0, D1, D2)

  공급량: supply = [30, 40]
  수요량: demand = [20, 25, 25]

  단위 운송비 (cost[i][j] = 공급지 i → 수요지 j 비용):
           D0   D1   D2
    S0  [  2,   3,   1 ]
    S1  [  5,   4,   8 ]

  총 운송비를 최소화하시오.

  힌트1: x = m.addMVar((2, 3), ...)   # 2×3 행렬 변수
  힌트2: 공급 제약: x.sum(axis=1) <= supply
  힌트3: 수요 제약: x.sum(axis=0) >= demand
  힌트4: 목적함수: (cost * x).sum()  — 원소별 곱 후 합산
"""

import gurobipy as gp
from gurobipy import GRB
import numpy as np

supply = np.array([30, 40])
demand = np.array([20, 25, 25])
cost   = np.array([[2, 3, 1],
                   [5, 4, 8]])

# Model 선언
m3 = gp.Model("problem3")

# 결정 변수 선언
x = m3.addMVar((2, 3), name="x", lb=0)

# 제약조건 추가
m3.addConstr(x.sum(axis=1) <= supply, name="supply_constraint")
m3.addConstr(x.sum(axis=0) >= demand, name="demand_constraint")

# 목적함수 설정
m3.setObjective((cost * x).sum(), GRB.MINIMIZE)

# 최적화
m3.optimize()

# 결과 출력
if m3.status == GRB.OPTIMAL:
    print("Optimal transportation plan (x):")
    print(np.round(x.X, 1))
    print(f"Minimum total transportation cost: {m3.objVal:.1f}")
else:
    print("No optimal solution found.")

    