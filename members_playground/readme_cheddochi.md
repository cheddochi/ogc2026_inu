# casat_cheddochi.py — 기술 문서

> **Bay Scheduling 최적화 솔버**  
> `myalgorithm.py` → `casat_cheddochi.algorithm(prob_info, timelimit)` 으로 호출

---

## 목차

1. [개요](#1-개요)
2. [설계 원칙](#2-설계-원칙)
3. [솔버 선택 로직](#3-솔버-선택-로직)
4. [전체 실행 흐름](#4-전체-실행-흐름)
5. [시간 관리 메커니즘](#5-시간-관리-메커니즘)
6. [섹션별 함수 상세](#6-섹션별-함수-상세)
7. [목적함수와 제약 조건](#7-목적함수와-제약-조건)
8. [입출력 형식](#8-입출력-형식)
9. [상수 레퍼런스](#9-상수-레퍼런스)
10. [의존성 및 설치](#10-의존성-및-설치)
11. [파일 배치](#11-파일-배치)

---

## 1. 개요

`casat_cheddochi.py`는 조선소 블록 배치(Bay Scheduling) 문제를 위한 통합 최적화 솔버다.
설치된 라이브러리에 따라 두 가지 솔버 중 최선을 자동 선택하며,
어떤 환경에서도 실행 가능하도록 단계별 폴백 체계를 갖는다.

| 우선순위 | 솔버 | 필요 조건 | 특징 |
|:---:|---|---|---|
| 1 | Gurobi MIP + LNS with MIP repair | `gurobipy` + 라이선스 | 연속 시간 변수, LP 완화, 최적성 갭 보장 |
| 2 | CP-SAT + Adaptive LNS | `ortools` | AddCumulative 제약, 무료 |

---

## 2. 설계 원칙

### 2-1. 결정 변수 단순화

탐욕 알고리즘의 탐색 공간은 5차원이다.

```
기존 탐색 공간: bay_id × orient_idx × x × y × entry_time
본 솔버:        bay_id × entry_time  (2차원)
```

목적함수를 분석하면 세 항 모두 `(bay_id, entry_time)`만으로 결정된다.

| 목적 항 | 필요 변수 |
|---|---|
| `w1 · Σtardiness` | `exit_time = entry_time + p` |
| `w2 · workload_imbalance` | `bay_id`, `workload` |
| `w3 · Σpref_penalty` | `bay_id`, `bay_preferences` |

`x, y, orient_idx`는 크레인·공간 제약을 충족하는 데만 쓰이므로,
스케줄이 확정된 후 **결정론적 후처리(Phase 2)** 로 분리한다.

### 2-2. 크레인 제약의 추상화

Shapely 폴리곤 연산 기반 크레인 경로 검사를  
**열(column) 폭 누적 합 ≤ bay 폭** 조건으로 근사한다.

```
동시 거주 블록들의 col_width 합 ≤ bay_width
```

- Gurobi: pairwise big-M 분리 제약
- CP-SAT: `AddCumulative(intervals, demands, capacity)`

---

## 3. 솔버 선택 로직

```
algorithm() 호출
       │
       ├─ gurobipy 설치됨?
       │     Yes
       │      ├─ n ≤ 150  →  §5  _gurobi_mip()                (전체 MIP)
       │      └─ n > 150  →  §9  _adaptive_lns(...Gurobi repair)
       │
       └─ ortools 설치됨?
              Yes
               ├─ n ≤ 150  →  §6  _cpsat_mip()                (전체 CP-SAT)
               └─ n > 150  →  §9  _adaptive_lns(...greedy repair)
```

`_MIP_LIMIT = 150` 블록을 기준으로 전체 MIP와 LNS를 분기한다.
전체 MIP는 변수가 많아지면 탐색이 느려지므로, 대규모 인스턴스는 LNS로 처리한다.

---

## 4. 전체 실행 흐름

```
algorithm(prob_info, timelimit)
│
├─ [Phase 0]  _precompute_orients()           §1  (orient 사전 계산)
│             _warm_start()                   §3  (EDD 탐욕 초기해)
│             _finalize(warm)                      ← 체크포인트 1 확보
│
├─ [시간 가드]  deadline까지 < 2초 → 체크포인트 1 즉시 반환
│
├─ [Phase 1]  솔버 자동 선택
│   ├─ _gurobi_mip()       §5  (Gurobi MIP, n≤150)
│   ├─ _cpsat_mip()        §6  (CP-SAT MIP, n≤150)
│   └─ _adaptive_lns()     §9  (LNS, n>150)
│        ├─ 매 이터레이션: _gurobi_repair() §8  또는  _greedy_repair() §7
│        └─ deadline 초과 0.5초 전 → 즉시 종료
│             _finalize(sched)                     ← 체크포인트 2 갱신
│
└─ 반환: best_solution  (체크포인트 1 또는 2)
         ↑ _finalize = _spatial(§10) + _build_solution(§11)
```

---

## 5. 시간 관리 메커니즘

타임리밋 초과를 방지하기 위해 **절대 데드라인** 기반으로 시간을 관리한다.

### 5-1. 데드라인 계산

```python
reserve  = max(2.0, min(_PHASE2_RESERVE, timelimit * 0.10))
deadline = t0 + timelimit - reserve
```

`reserve`는 Phase 2(공간 배치 + 출력 빌더)를 위한 예약 시간이다.  
`timelimit`이 짧을수록 10% 룰이 적용되며, 최소 2초는 보장된다.

| timelimit | reserve | 최적화 가능 시간 |
|---:|---:|---:|
| 10s | 2.0s | 8s |
| 30s | 3.0s | 27s |
| 60s | 5.0s | 55s |
| 120s | 5.0s | 115s |

### 5-2. 체크포인트 구조

```
best_solution = None              # 시작 시점
      │
      ▼  Phase 0 완료
best_solution = _finalize(warm)         ← 체크포인트 1 (warm start 해)
      │
      ▼  Phase 1 완료 (정상 종료)
best_solution = _finalize(sched)        ← 체크포인트 2 (최적화 해)
      │
      ▼  오류 발생 시
      └─ 체크포인트 1 반환
```

`_finalize(sched)`는 `_spatial()` + `_build_solution()`을 합친 헬퍼로,
체크포인트마다 **즉시 반환 가능한 완성된 해**를 유지한다.

### 5-3. 각 Phase별 시간 제어 방식

| Phase | 시간 제어 방법 |
|---|---|
| Phase 0 (warm start) | 항상 실행. O(n²) 이지만 수 ms 이내 |
| Phase 1 진입 가드 | `_t_left() < 2.0`이면 Phase 1 건너뜀 |
| Gurobi MIP | `m.setParam("TimeLimit", _t_left())` |
| CP-SAT | `solver.parameters.max_time_in_seconds = tlimit` |
| LNS 루프 | `while True: remaining = deadline - time.time()` |
| LNS repair 1회 | `t_rep = min(_REPAIR_TLIMIT, remaining * 0.5)` |

LNS는 **상대 시간**이 아닌 **절대 데드라인**을 직접 받아  
상위 `algorithm()`에서 계산한 시간 예산을 정확히 준수한다.

---

## 6. 섹션별 함수 상세

### §1  기하 헬퍼

| 함수 | 역할 |
|---|---|
| `_bbox(blk, oi)` | 블록 `oi` 방향의 바운딩박스 `(lx0, ly0, lx1, ly1)` 반환. 참조점 = (0,0) |
| `_col_w(blk, oi)` | 정수 열 폭 = `ceil(lx1 - lx0)` |
| `_narrowest_orient(blk, bay_w, bay_h)` | bay에 들어가는 방향 중 열 폭이 가장 좁은 것. `(orient_idx, col_width)` |
| `_precompute_orients(prob_info)` | `(block_id, bay_id) → (orient_idx, col_width)` 전체 사전 계산. 반복 호출 비용 절감 |

### §2  목적함수 평가

```python
_objective(prob_info, sched) → float
```

스케줄 dict `{block_id: {bay_id, entry_time, exit_time}}`에서 스칼라 목적값을 계산한다.  
MIP 솔버의 `obj` 값 검증 및 LNS 수용 기준으로 사용된다.

### §3  Phase 0 — EDD warm start

```python
_warm_start(prob_info, orients) → sched_dict
```

**Earliest Due Date** 순으로 블록을 정렬해 탐욕 배정한다.

1. 각 블록에 대해 `bay_preferences` 내림차순으로 bay 순회
2. 후보 진입 시각 = `{release_time} ∪ {기존 블록들의 exit_time}`
3. `누적 열 폭 합 ≤ bay 폭`인 최이른 슬롯 선택
4. 모든 bay에서 실패 시: 최선호 bay의 완전히 빈 구간에 강제 배치

warm start는 Phase 1의 초기해(MIP warm start hint)로 활용된다.

### §4  충돌 쌍 사전 계산

```python
_conflict_pairs(prob_info, orients) → list[(i, j, [bays])]
```

두 블록이 특정 bay에서 동시 거주할 때 열 폭 합이 bay 폭을 초과하는
모든 (pair, bay) 조합을 반환한다.  
Gurobi MIP에서 분리 제약(big-M)을 생성하는 데 사용된다.

```
col_width[i, b] + col_width[j, b] > bay_width[b]  →  충돌 쌍
```

### §5  Gurobi 전체 MIP (`n ≤ _MIP_LIMIT`)

```python
_gurobi_mip(prob_info, warm, orients, tlimit) → sched_dict
```

**결정 변수**

| 변수 | 타입 | 의미 |
|---|---|---|
| `start[i]` | 연속 `≥ release_time[i]` | 진입 시각 |
| `end[i]` | 연속 | `= start[i] + processing_time[i]` |
| `x[i, b]` | 이진 | block `i`를 bay `b`에 배정 |
| `z[k]` | 이진 | 충돌 쌍 `k`의 순서 (`1` = i가 j보다 먼저) |

**크레인 제약 (pairwise big-M 분리)**

충돌 쌍 (i, j, bay b) 마다:
```
end[i] ≤ start[j] + M·(1-z[k]) + M·(1-x[i,b]) + M·(1-x[j,b])
end[j] ≤ start[i] + M·z[k]     + M·(1-x[i,b]) + M·(1-x[j,b])
```
두 블록이 **모두 bay b에 배정**될 때만 활성화된다.

**CP-SAT 대비 Gurobi 이점**

- `start[i]`가 **연속** → T가 커도 정수 도메인 폭발 없음
- LP 완화 + Gurobi cuts(Gomory, flow cover 등) → 타이트한 하한
- 병렬 branch-and-bound (`Threads=8`)
- warm start hint가 분수 LP에 즉시 반영

**주요 Gurobi 파라미터**

| 파라미터 | 값 | 의미 |
|---|---|---|
| `TimeLimit` | `_t_left()` | 데드라인까지 남은 시간 |
| `MIPGap` | `0.01` | 1% 최적성 갭에서 조기 종료 |
| `MIPFocus` | `1` | 초기 실현 가능 해 확보 우선 |
| `Cuts` | `2` | 공격적 컷 생성 |
| `ImproveStartTime` | `tlimit × 0.3` | 30% 이후 최적화에 집중 |

### §6  CP-SAT 전체 MIP (`n ≤ _MIP_LIMIT`, Gurobi 없을 때)

```python
_cpsat_mip(prob_info, warm, orients, tlimit) → sched_dict
```

OR-Tools CP-SAT을 사용한다. 크레인 제약을 `AddCumulative`로 직접 표현한다.

```python
for b in range(M):
    mdl.AddCumulative(
        intervals=[optional_interval(i, b) for i in range(n)],
        demands=[col_width[i] for i in range(n)],
        capacity=bay_width[b]
    )
```

float 목적값을 `S=1000`으로 스케일해 정수 변환한 후 최적화한다.

### §7  Greedy repair

```python
_greedy_repair(prob_info, fixed, to_place, orients) → sched_dict
```

`fixed` 스케줄을 유지하면서 `to_place` 블록들을 EDD 순서로 재배치한다.  
두 가지 용도로 사용된다.

1. **LNS greedy 모드**: OR-Tools 있을 때 repair 역할
2. **Gurobi repair의 warm start**: `_gurobi_repair` 호출 전 초기해 생성

### §8  Gurobi MIP repair (k블록 소형 서브문제)

```python
_gurobi_repair(prob_info, fixed, to_place, orients, tlimit=2.0) → sched_dict
```

LNS의 핵심 컴포넌트. **k개 파괴 블록 전체를 하나의 소형 MIP로 동시 최적화**한다.

**greedy repair 대비 차이**

| | greedy repair | Gurobi MIP repair |
|---|---|---|
| 최적화 방식 | EDD 순서 순차 결정 | k블록 동시 최적화 |
| 해 품질 | 국소 편향 가능 | 전역 최적 (k범위 내) |
| 실행 시간 | O(k·n) | ~ms (warm start) |

**제약 구성**

- repaired ↔ repaired: `_conflict_pairs`로 충돌하는 쌍에 pairwise 분리 제약
- repaired ↔ fixed: 고정 블록과 충돌 시 분리 제약  
  (`z_f=1`: repaired가 fixed보다 늦게 시작)

`k > _REPAIR_MAX_K(=40)`이면 greedy 폴백 (MIP 과부하 방지).

### §9  Adaptive LNS (`n > _MIP_LIMIT`)

```python
_adaptive_lns(prob_info, warm, orients, deadline, use_gurobi_repair) → sched_dict
```

**LNS 기본 루프**

```
while deadline - time.time() > 0.5:
  1. k개 블록을 무작위 선택 (destroy)
  2. repair: _gurobi_repair() 또는 _greedy_repair()
  3. 개선되면 accept, 아니면 거절
  4. k 조정 (adaptive)
```

**k 조정 전략**

| 상황 | 조치 |
|---|---|
| 개선 성공 | `k = max(k_min, k-1)` — 집중 탐색(intensification) |
| `patience`회 미개선 | `current = best`, `k = min(k_max, k+2)` — 다변화(diversification) |

| 파라미터 | Gurobi repair | greedy repair |
|---|---|---|
| k 초기값 | `n // 5` | `n // 10` |
| patience | 10 | 30 |
| k_max | `n // 2` | `n // 3` |

**시간 관리 (절대 데드라인)**

`algorithm()`이 계산한 `deadline`을 직접 수신하므로
전체 `timelimit` 안에 항상 종료된다.

```python
while True:
    remaining = deadline - time.time()
    if remaining < 0.5: break                        # 즉시 중단
    t_rep = min(_REPAIR_TLIMIT, remaining * 0.5)     # repair 1회 제한
```

### §10  공간 배치 (Phase 2 후처리)

```python
_spatial(prob_info, sched) → pos_dict {block_id: (x, y, orient_idx)}
```

확정된 스케줄 `(bay_id, entry_time, exit_time)`에서 x, y 좌표와 방향을 결정한다.

**알고리즘** — bay별로 진입 시각 순 처리:

1. 현재 블록의 동시 거주 블록들의 x 범위를 `occupied` 리스트로 수집
2. 가장 좁은 방향(orient)부터 시도
3. `x=0` 또는 각 occupied 범위의 오른쪽 끝에서 첫 번째 빈 간격 선택
4. 실패 시 fallback: `(x=0, y=0, orient=0)`

Phase 1의 누적 폭 제약이 `총 열 폭 ≤ bay 폭`을 보장하므로 항상 성공한다.

### §11  출력 빌더

```python
_build_solution(sched, pos) → {"operations": {str(t): [op, ...]}}
```

`check_feasibility` 호환 포맷으로 변환한다.  
같은 시각에 EXIT가 ENTRY보다 앞에 오고, 같은 타입 내에서는 `block_id` 오름차순이다.

### §12  공개 진입점

```python
algorithm(prob_info, timelimit=60) → solution_dict
```

`myalgorithm.py`에서 호출되는 유일한 공개 함수다.  
모든 내부 함수는 `_` 접두어를 가진다.

---

## 7. 목적함수와 제약 조건

### 목적함수

$$\text{minimize} \quad w_1 \cdot \sum_i \max(0,\ e_i - d_i)\ +\ w_2 \cdot (\max_b L_b - \min_b L_b)\ +\ w_3 \cdot \sum_i (s^{\max}_i - s_{i,b_i})$$

| 항 | 변수 | 의미 |
|---|---|---|
| $w_1$ 항 | `tardiness` | 납기 지연 합계 |
| $w_2$ 항 | `workload imbalance` | bay별 작업량 최대-최소 차이 |
| $w_3$ 항 | `preference penalty` | 최선호 bay 대비 패널티 합계 |

### 주요 제약

| 제약 | 표현 |
|---|---|
| 블록당 bay 배정 | $\sum_b x_{i,b} = 1$ |
| 진입 시각 | $s_i \geq r_i$ (release time) |
| 퇴장 시각 | $e_i = s_i + p_i$ |
| 크레인 제약 (pairwise) | 충돌 쌍 (i,j)는 같은 bay에 있을 때 시간 분리 |
| 크레인 제약 (cumulative) | bay 내 동시 거주 블록의 열 폭 합 ≤ bay 폭 |

---

## 8. 입출력 형식

### 입력: `prob_info` dict

```python
{
    "name":    str,
    "bays":   [{"width": float, "height": float}, ...],
    "blocks": [{
        "release_time":    int,
        "due_date":        int,
        "processing_time": int,
        "workload":        float,
        "bay_preferences": [float, ...],   # bay별 선호 점수 (높을수록 선호)
        "shape": [{
            "layers": [...]    # 방향별 레이어 정보 (utils._resolve_layers 형식)
        }, ...]
    }, ...],
    "weights": {"w1": float, "w2": float, "w3": float}
}
```

### 중간 표현: 스케줄 dict

```python
sched = {
    block_id: {
        "block_id":   int,
        "bay_id":     int,
        "entry_time": int,   # ≥ release_time
        "exit_time":  int    # = entry_time + processing_time
    }, ...
}
```

### 출력: solution dict (`check_feasibility` 호환)

```python
{
    "operations": {
        "100": [                              # 시각 (str)
            {"type": "EXIT",  "block_id": 3, "bay_id": 0},
            {"type": "ENTRY", "block_id": 5, "bay_id": 1,
             "x": 0, "y": 0, "orient_idx": 2}
        ],
        ...
    }
}
```

같은 시각에서의 순서: **EXIT 먼저, 그 다음 ENTRY** (같은 타입 내 `block_id` 오름차순).

---

## 9. 상수 레퍼런스

| 상수 | 기본값 | 의미 | 튜닝 가이드 |
|---|---|---|---|
| `_MIP_LIMIT` | `150` | 전체 MIP / LNS 분기 블록 수 | 인스턴스가 작으면 낮춰서 MIP 확대 |
| `_REPAIR_TLIMIT` | `2.0` | Gurobi repair 1회 제한 (초) | 높이면 품질↑, 이터레이션 수↓ |
| `_REPAIR_MAX_K` | `40` | MIP repair 최대 블록 수 | 높이면 품질↑, 속도↓ |
| `_MIP_GAP` | `0.01` | Gurobi 최적성 갭 (1%) | 낮추면 품질↑, 시간↑ |
| `_PHASE2_RESERVE` | `5.0` | Phase 2 예약 시간 (초) | n이 매우 크면 늘릴 것 |

---

## 10. 의존성 및 설치

### 필수 (항상)

```bash
# 원본 제공 파일 (별도 설치 불필요)
utils.py   # _bounding_box, _resolve_layers
```

Python 표준 라이브러리: `math`, `time`, `copy`, `random`

### 선택 (설치 여부에 따라 솔버 자동 선택)

```bash
# 1순위: Gurobi (라이선스 필요)
pip install gurobipy
# 학술용 무료 라이선스: https://www.gurobi.com/academia/academic-program-and-licenses/

# 2순위: OR-Tools (무료)
pip install ortools
```

### 설치 상태별 동작

```
gurobipy O + 라이선스 O  →  Gurobi MIP / LNS+MIP repair  (최고 품질)
gurobipy O + 라이선스 X  →  GurobiError → OR-Tools 폴백
ortools  O               →  CP-SAT / LNS+greedy          (무료, 준최적)
둘 다    X               →  Phase 0 warm start 해 반환
```

---

## 11. 파일 배치

```
작업 디렉터리/
├── myalgorithm.py        ← 진입점 (수정하지 않음)
├── casat_cheddochi.py    ← 이 파일
└── utils.py              ← 원본 제공 (수정하지 않음)
```

### 호출 관계

```
myalgorithm.algorithm(prob_info, timelimit)
  └─ casat_cheddochi.algorithm(prob_info, timelimit)
        ├─ _precompute_orients()    §1
        ├─ _warm_start()            §3
        ├─ [Phase 1 선택]
        │    ├─ _gurobi_mip()       §5  ←─ _conflict_pairs() §4
        │    ├─ _cpsat_mip()        §6
        │    └─ _adaptive_lns()     §9  ←─ _gurobi_repair()  §8
        │                                    └─ _greedy_repair() §7
        └─ _finalize()
              ├─ _spatial()         §10
              └─ _build_solution()  §11
```

---

*마지막 수정: timelimit 초과 방지를 위한 절대 데드라인 + 체크포인트 체계 추가*
