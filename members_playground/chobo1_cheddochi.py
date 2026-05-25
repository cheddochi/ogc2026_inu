# ══════════════════════════════════════════════════════════════
# 문제 1  ★☆☆  선형계획법(LP) 기초 — 생산량 결정
# ══════════════════════════════════════════════════════════════
"""
[문제 1] 두 제품 A, B를 생산하는 공장이 있다.

  제약 조건
  ─────────
  · 기계 시간:  3·x_A + 2·x_B  ≤  120  (시간/주)
  · 노동 시간:  1·x_A + 2·x_B  ≤  80   (시간/주)
  · 생산량 비음: x_A, x_B ≥ 0

  목적 함수
  ─────────
  · 이익 최대화:  max  5·x_A + 4·x_B

  (1) Gurobi 모델을 작성하여 최적 생산량과 최대 이익을 구하시오.
  (2) model.optimize() 호출 후 최적해를 출력하시오.
"""

# 여기에 코드를 작성하시오.
import gurobipy as gp
from gurobipy import GRB

# TODO: 모델 생성, 변수 추가, 제약 추가, 목적함수 설정, 최적화, 결과 출력
m1 = gp.Model("problem1")

# ... (코드 작성)
x_A = m1.addVar(name="x_A", lb=0)
x_B = m1.addVar(name="x_B", lb=0)

m1.addConstr(3*x_A + 2*x_B <= 120,  name="machine_time")
m1.addConstr(1*x_A + 2*x_B <= 80,   name="labor_time")

m1.setObjective(5*x_A + 4*x_B, GRB.MAXIMIZE)

m1.optimize()

if m1.status == GRB.OPTIMAL:
    print(f"Optimal production of A:    {x_A.x}")
    print(f"Optimal production of B:    {x_B.x}")
    print(f"Maximum profit:             {m1.objVal}")
else:
    print("No optimal solutionn found.")

