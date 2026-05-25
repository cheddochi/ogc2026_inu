# ══════════════════════════════════════════════════════════════
# 문제 2  ★☆☆  변수 타입 — 정수계획법(ILP)
# ══════════════════════════════════════════════════════════════
"""
[문제 2] 배낭 문제 (Knapsack Problem)

  물건 5개의 무게(w)와 가치(v):
    물건  무게  가치
      0    2    3
      1    3    4
      2    4    5
      3    5    8
      4    9    10

  배낭 최대 무게 = 10

  물건을 담거나(1) 안 담거나(0), 무게 합계 ≤ 10 을 만족하면서
  가치 합계를 최대화하시오.

  힌트: 변수 선언 시  vtype=GRB.BINARY  사용
"""
import gurobipy as gp
from gurobipy import GRB

# 비율 및 조건
weights = [2, 3, 4, 5, 9]
values = [3, 4, 5, 8, 10]
capacity = 10

# Model 선언
m2 = gp.Model("problem2")

# 결정 변수 선언
x = [0, 0, 0, 0, 0] # 배낭에 담을 각 물건의 갯수

for i in range(5):
    x[i] = m2.addVar(vtype=gp.GRB.BINARY, name=f"x_{i}")

# 제약식 추가
m2.addConstr(gp.quicksum(weights[i] * x[i] for i in range(5)) <= capacity, name="capacity_constraint")  

# 목적함수 설정
m2.setObjective(gp.quicksum(values[i] * x[i] for i in range(5)), GRB.MAXIMIZE)

# 최적화
m2.optimize()

# 결과 출력
if m2.status == GRB.OPTIMAL:
    print("Optimal solution found:")
    for i in range(5):
        print(f"Item {i}: {'Included' if x[i].x > 0.5 else 'Not included'}")
    print(f"Maximum value: {m2.objVal}")
else:
    print("No optimal solution found.") 



