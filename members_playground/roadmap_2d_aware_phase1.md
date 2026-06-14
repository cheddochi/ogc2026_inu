# 2D-aware Phase 1 재설계 로드맵

> 이 문서는 `casat_cheddochi.py`를 2D(크레인-feasible) 관점에서 단계적으로
> 개선하기 위한 작업 계획이다. **Phase 1(이번 세션에서 완료)** 은 §10
> `_spatial`(Phase 2 후처리)을 x·y 양축을 쓰는 2D bottom-left-fill로
> 재작성하고, 그 결과를 train set으로 검증했다. 나머지 Phase 2~4는
> 다음 세션에서 진행할 작업이다.
>
> **중요**: `_FAST_GREEDY_THRESHOLD = 1` (casat_cheddochi.py 49행)은
> 현재 그대로 유지된다 — 즉 프로덕션 경로는 여전히 `baseline_greedy`로
> 안전하게 폴백한다. 아래 Phase 1~4는 모두 "활성화되지 않은" 코드 경로
> (`_warm_start` → Phase1 MIP/LNS → `_spatial`)에 대한 개선이며, 이
> 경로가 train set에서 충분히 높은 통과율을 달성하기 전까지는 프로덕션
> 동작에 영향이 없다.

---

## 배경

이전 세션에서 도출된 결론:

> 현재 아키텍처(1D column-width cumulative)에서 메타파라미터·휴리스틱
> 조정만으로는 추가 격차를 좁히기 어렵다. CP-SAT/LNS 모델에 y축 점유까지
> 포함한 2D-aware 모델로 재설계해야 진전이 가능하다.

Phase 1의 솔버(`_cpsat_mip`, `_gurobi_mip`, `_adaptive_lns`)는 각 블록을
"narrowest-fitting 방향의 열 폭(`cw`)"만으로 표현하고, 시간이 겹치는
블록들의 `cw` 합이 bay 폭을 넘지 않도록 `AddCumulative`(CP-SAT) /
pairwise big-M(Gurobi)로 제약한다 — **1차원(폭) 제약**이다. 이 모델이
만든 스케줄은 "폭 합이 bay 폭을 넘지 않는다"는 것만 보장하며, y축 점유나
실제 2D 배치 가능성은 전혀 보장하지 않는다.

---

## Phase 1 (완료) — `_spatial` 2D bottom-left-fill 재작성

### 변경 내용

`_spatial`(§10)을 다음과 같이 재작성했다:

- bay별로 진입 시각 순으로 블록을 처리
- 각 블록에 대해, 시간 구간이 겹치는 이미 배치된 블록들("neighbors")의
  AABB(`Block.bounding_rect()`)를 수집
- `_col_w`(열 폭) 오름차순으로 방향(orient)을 순회하며, bay 크기를
  초과하지 않는 방향만 시도
- `baseline_greedy._candidate_positions`가 생성하는 **x·y 양축**
  bottom-left-fill 후보 `(x, y)` 중, 자신의 AABB가 모든 neighbor AABB와
  겹치지 않는 첫 후보를 채택
- 모든 후보가 막힌 경우, neighbor를 무시하고 bay 경계 내부에 정수 좌표로
  들어가는 방향/위치를 우선 채택 (그래도 없으면 최소 면적 방향을 원점에
  배치하는 최후 안전망)

### 정합성 근거 (AABB-분리 충분조건)

시간 구간이 겹치는 두 블록의 AABB가 분리되어 있고 각자 bay 경계 내부에
있으면, AABB는 모든 레이어(층)의 합집합이므로 어떤 레이어 쌍도 겹칠 수
없다 — 즉 `check_entry`/`check_exit`/`check_collisions`(Stage2~4)가
항상 통과한다. `_spatial`은 시간이 겹치는 모든 블록 쌍에 대해 이
충분조건을 보장하도록 설계되었다.

또한 "고정된 neighbor 배치"에 대해, 실수 좌표상 겹치지 않는 배치가
존재한다면 `_candidate_positions`의 corner-point 후보 집합에 반드시
그 배치가 포함된다는 것을 "bottom-left로 슬라이드" 논증으로 증명했다
(corner-point BLF의 완전성). 즉 `_spatial`의 탐색 로직 자체는 주어진
순서·neighbor 배치에 대해 최선을 다한다.

### 검증 결과 (train set, 40개 문제)

| 스케줄 소스 | PASS / 40 |
|---|---|
| 기존 `_spatial` (X축 전용, 재작성 전) | 0 / 40 |
| 새 `_spatial` + `_warm_start` 스케줄만 | 4 / 40 |
| 새 `_spatial` + 실제 Phase 1 스케줄 (CP-SAT n≤150 / LNS+greedy n>150, 8s) | **3 / 40** |

X축 전용 → X·Y 양축으로의 전환만으로 명확한 정합성 개선이 있음을
확인했다. 그러나 대다수 문제는 여전히 Stage2(충돌/스윕, 또는 bay 경계
초과)에서 실패한다. 아래에서 그 원인을 분석한다.

### 남은 실패의 세 가지 원인 (모두 Phase 1 영역)

#### (C) `_narrowest_orient`의 "맞는 방향 없음" 폴백 — 즉시 수정 가능한 핫스팟

`_narrowest_orient`(67행)은 bay (`bay_w`, `bay_h`)에 들어가는 방향 중 가장
좁은 `cw`를 찾는다. 그런데 **어떤 방향도 들어가지 않으면**
(`best_cw == inf`) 다음과 같이 **무조건 orient 0의 cw를 반환**한다:

```python
if best_cw == float("inf"):
    best_oi, best_cw = 0, _col_w(blk, 0)
```

즉 `_precompute_orients`가 만드는 `orients[(i, b)]`는 "block i가 bay b에
**전혀 들어갈 수 없는 경우에도** 항상 어떤 `(orient_idx, cw)` 값을
반환"한다 — Phase 1(`_warm_start`, `_cpsat_mip`, `_gurobi_mip`)은 이
`cw`만 보고 "폭이 맞으면 배정 가능"이라고 판단하므로, **block이 해당
bay에 결코 들어갈 수 없는데도 그 bay에 배정될 수 있다.**

실제 사례 (`train/prob_9.json`, block 95):

- bay 0 = 107 × 17. block 95의 8개 방향 모두 bbox 높이 ≥ 20.50 > 17 —
  **어떤 방향으로도 bay 0에 들어갈 수 없다.**
- 그런데 `orients[(95, 0)] = (0, 21)` (orient 0의 cw=21 ≤ bay_w=107 이므로
  1D 폭 제약은 통과) → Phase 1이 block 95를 bay 0에 배정.
- `_spatial`은 (정상적으로) 이 블록을 bay 0의 어떤 위치에도 넣을 수
  없고, 최후 안전망으로 원점에 배치 → `check_feasibility`가
  "block 95 exceeds bay boundary (area=111.20)"로 실패.
- `prob_14`(block 144), `prob_15`(block 82)도 동일한 패턴.

**제안 수정 (저비용, Phase 1에 국한)**: `_narrowest_orient`이 "맞는
방향 없음"을 `cw = bay_w + 1`(또는 `None`) 같은 **명시적으로
infeasible한 값**으로 반환하도록 변경하고, 이를 사용하는 곳
(`_warm_start`의 bay 순회, `_cpsat_mip`/`_gurobi_mip`의 `in_b[i][b]`
도메인, `_conflict_pairs`)에서 해당 (block, bay) 조합을 **배정 후보에서
제외**한다. 이는 2D no-overlap 모델링 없이도 (C) 유형의 실패를 완전히
제거할 수 있는, 독립적이고 작은 변경이다 — Phase 2 작업 중 가장 먼저
처리할 항목으로 권장.

#### (A) 정수 좌표 반올림 간극 (integer-rounding gap)

`check_feasibility`는 좌표를 `x = int(round(x)), y = int(round(y))`로
반올림한다(utils.py 1154행 등). 따라서 `_spatial`이 만드는 `(x, y)`는
실질적으로 **정수**여야 한다.

예 (`train/prob_1.json` block 84, bay 1, 54×18):

- orient 2/6 (가장 좁은 `cw`)의 bbox 높이 = 17.72, bay 높이 = 18 →
  실수 좌표로는 "맞는" 방향이지만, `y`가 만족해야 하는 범위는
  `ceil(-ly0) <= y <= floor(bay_h - ly1)` = `[14, 13]` — **공집합**.
- 즉 `_candidate_positions`가 이 방향에 대해 빈 후보 목록을 반환하는
  것은 버그가 아니라, 해당 방향이 **정수 격자에서는 이 bay에 들어갈 수
  없다**는 정확한 판정이다.

Phase 1의 `cw` 계산(`_cpsat_mip` 321행: `cw[i] = min(orients[(i,b)][1]
for b in range(M))`)은 폭(1차원)만 정수로 다루고 높이는 전혀 고려하지
않으므로, 이런 "높이 쪽 정수 간극"으로 인한 배치 불가능을 Phase 1이
미리 걸러낼 방법이 없다.

#### (B) 단편화(fragmentation) — non-backtracking greedy의 한계

`train/prob_1.json` block 84 (bay 1, 54×18, entry=32, exit=40)는 시간이
겹치는 neighbor 5개(블록 65, 38, 18, 4, 1; 총 면적 ≈ 485.75 / 972)가
이미 배치된 상태에서 배치를 시도한다. orient 0 (`cw=18`,
bbox=(-13.64, 0, 4.08, 5.26))을 포함한 모든 "bay에 맞는" 방향에 대해,
**어떤 정수 `(x, y)`를 골라도 blocks 65/18/1 중 하나와 반드시 겹친다**는
것을 직접 좌표 계산으로 증명했다 (해당 시점에 이미 배치된 블록들이 만든
빈 공간의 형태가 block 84의 어떤 방향과도 맞지 않음).

이는 `_spatial`의 탐색 누락이 아니라, **Phase 1이 만든 1D-feasible
스케줄이 2D 배치를 보장하지 않기 때문**에 발생하는 근본적인 문제다.
single-pass greedy(non-backtracking)인 `_spatial`은 이미 배치한 블록의
위치를 되돌릴 수 없으므로, Phase 1 스케줄 자체가 2D-feasible하지
않으면 구조적으로 해결할 수 없다.

→ **결론**: `_spatial`은 "주어진 스케줄에 대해 할 수 있는 최선"을
하도록 올바르게 작성되었다. 추가 개선은 **Phase 1(스케줄링 모델)이
2D 점유를 인식하도록 재설계**해야 가능하다 — 아래 Phase 2~4.

---

## Phase 2 — Phase 1 솔버의 2D-aware 용량 모델

### 현재 모델의 한계

1. **1차원 폭 제약뿐**: `_cpsat_mip`의 `AddCumulative(ivs, dems,
   bay_width)` (348행)은 시간이 겹치는 블록들의 `cw` 합만 제한한다.
   y축(bay 높이) 점유는 전혀 모델링되지 않는다.
2. **`cw` 계산이 bay-독립적**: `_cpsat_mip` 321행은
   `cw[i] = min(orients[(i,b)][1] for b in range(M))` — 즉 **어떤
   bay에 배정되더라도 전역 최소 열 폭**을 사용한다. 반면 `_warm_start`
   (136행)는 `orients[(bi, bay_id)]`로 **배정된 bay 기준**의 cw를 쓴다.
   - 만약 블록 i의 전역 최소 cw를 만드는 방향이 bay A에서만 나오고,
     실제로는 bay B에 배정되었다면, bay B의 `AddCumulative`에 들어가는
     `dems[i]`는 bay B 기준으로는 과소평가된 값일 수 있다 — 즉 Phase 1
     모델이 "실제보다 더 많이 들어갈 수 있다"고 착각할 수 있다.
   - 이 불일치는 (A)/(B) 두 실패 모두를 악화시킬 수 있는 잠재적 원인이다.
     2D 모델로 가기 전에 우선 **bay-종속 `cw[i][b] = orients[(i,b)][1]`**
     로 교체하는 것이 작은 첫 단계가 될 수 있다.

### 제안 방향

0. **최우선 (최저비용)**: 위 (C)에서 설명한 `_narrowest_orient`의
   "맞는 방향 없음" 폴백을 수정하여, 어떤 방향으로도 들어가지 않는
   (block, bay) 조합을 Phase 1의 배정 후보에서 제외한다. 2D 모델링
   없이도 적용 가능하며, train set 일부 실패(예: prob_9/14/15)를
   즉시 해소할 수 있다.
1. **단기 (저비용)**: `cw[i]`를 bay-종속으로 교체
   (`cw[i][b] = orients[(i,b)][1]`)하고 `AddCumulative`의 `dems`를
   `in_b[i][b]`에 따라 선택하도록 수정 (`AddElement` 또는
   bay별로 별도 `OptionalIntervalVar` 사용 — 현재 구조와 호환).
2. **중기**: 각 (block, bay) 쌍에 대해 폭(`cw`)과 높이(`ch`, 같은
   방향의 bbox 높이)를 함께 전달하고, bay별로 **2D no-overlap**을
   표현. CP-SAT는 `AddNoOverlap2D(x_intervals, y_intervals)`를
   제공하므로, 시간이 겹치는 블록들에 대해
   - x-interval: `[x_i, x_i + cw_i]` (x_i는 새 IntVar, 도메인
     `[0, bay_w - cw_i]`)
   - y-interval: `[y_i, y_i + ch_i]` (y_i는 새 IntVar, 도메인
     `[0, bay_h - ch_i]`)
   를 만들고, **시간 구간이 겹치는 블록 쌍에만** 2D 분리를 강제하면
   된다 (시간이 겹치지 않으면 같은 자리를 재사용해도 무방).
   - 주의: `AddNoOverlap2D`는 "같은 평면 위 모든 박스가 서로
     안 겹친다"를 의미하므로, 시간이 겹치지 않는 블록 쌍까지 분리
     강제하면 과도하게 제약적이다. 대신 **conflict pair별로
     `AddNoOverlap2D`를 거는 대신, "두 박스가 모두 활성(active)인
     시간 구간 동안만 분리"** 되도록 `OptionalIntervalVar` +
     `(i,b)`별 `x_i, y_i` 변수 조합으로 직접 분리(big-M 또는
     `AddForbiddenAssignments`류)를 구성해야 한다. 이 부분이 Phase 2의
     핵심 설계 작업이다.
3. **정수 간극(A) 대응**: `x_i`, `y_i`를 IntVar로 두면 자연히 정수
   해만 나오므로, (A)에서 식별한 "실수로는 맞지만 정수로는 안 맞는"
   방향은 CP-SAT 단계에서 이미 제외된다 — 즉 Phase 2 모델은 (A)
   문제를 구조적으로 해결한다.
4. `_gurobi_mip`(§5)에도 동일한 사상의 pairwise big-M 2D 분리 제약을
   추가해야 한다 (현재는 1D만).

### `_spatial`과의 관계

Phase 2가 도입되면 `_spatial`은 "정확한 `(x, y, orient)`를 이미 풀어낸
Phase 1 결과를 거의 그대로 통과"시키는 역할로 축소될 수 있다 (필요시
정렬/정규화만). 다만 모델 크기·시간 제한으로 Phase 1이 일부 블록의
`(x, y)`를 결정하지 못하는 경우를 대비해, 현재의 2D bottom-left-fill
`_spatial`은 **폴백으로 계속 유지**하는 것을 권장한다.

---

## Phase 3 — LNS repair의 2D-aware화

`_adaptive_lns`(§9)의 `_greedy_repair`(§7) / `_gurobi_repair`(§8)는
destroy된 블록들을 다시 배정할 때 Phase 1과 동일한 1D 용량 모델을
사용한다. Phase 2에서 Phase 1의 전체 MIP가 2D-aware로 바뀌면:

1. `_greedy_repair`도 같은 2D 제약(시간이 겹치는 블록과의 `(x,y,cw,ch)`
   분리)을 만족하는 배정만 후보로 인정해야 한다. 가장 간단한 방법은
   각 destroy 블록을 재배정할 때 `_spatial`과 동일한 bottom-left-fill
   탐색으로 `(x,y,orient)` 후보를 얻고, 그 좌표를 기반으로 분리
   제약을 평가하는 것.
2. `_gurobi_repair`(소형 서브문제 MIP)에는 Phase 2와 동일한 pairwise
   2D big-M 분리 제약을 추가.
3. `_objective` 평가는 변경 없음 (스케줄 기반 목적함수는 그대로 유효).

이 단계의 목표는 "LNS가 만드는 중간 해도 `_spatial`이 2D-feasible하게
배치할 수 있는 스케줄"이 되도록 보장하는 것이다.

---

## Phase 4 — 재튜닝 및 `_FAST_GREEDY_THRESHOLD` 재검토

Phase 2~3 완료 후:

1. train set 40개 전체에 대해 `_warm_start` → Phase 1(2D-aware) →
   `_spatial` 파이프라인의 feasibility/objective를 `baseline_greedy`와
   비교.
2. 충분히 높은 통과율(예: 전 구간 100% feasible, objective가
   `baseline_greedy` 대비 우위)이 확인되면, `_FAST_GREEDY_THRESHOLD`를
   `1`에서 점진적으로 상향 조정 (예: 작은 `n`부터 단계적으로 Phase 0-2
   경로를 활성화).
3. 시간 제한(`tlimit`) 대비 CP-SAT/LNS의 2D 모델 solve 시간을 재측정하고,
   `_REPAIR_TLIMIT` 등 시간 관리 상수를 재조정.
4. 위 모든 변경은 별도 세션에서, 단계별로 train set 검증을 거쳐 진행한다.

---

## 요약 체크리스트 (다음 세션 시작점)

- [x] Phase 1: `_spatial` 2D bottom-left-fill 재작성 + train set 검증
- [x] Phase 2-0: `_narrowest_orient`의 "맞는 방향 없음" 폴백 수정 —
      어떤 방향으로도 안 들어가는 (block, bay)를 배정 후보에서 제외
      (저비용, 즉시 적용 가능)
- [x] Phase 2-1: `_cpsat_mip`/`_gurobi_mip`의 `cw[i]`를 bay-종속으로 교체
- [x] Phase 2-2: `_spatial`을 진입시각 postponement 기반 2D
      bottom-left-fill로 재작성 (AABB-분리 충분조건으로 Stage2~4 항상
      통과 보장) — **train set 40/40 feasible 달성** (iter2,
      objective 917,417,673 / T 90,704)
- [x] Phase 3: `_greedy_repair`/`_gurobi_repair`를 2D 제약과 정합되게 수정 —
      **`_repair_capacity`(§9.5, 신규) 추가**. `_conflict_pairs` 기반
      pairwise 분리(`_gurobi_repair`/`_gurobi_mip`/`_cpsat_mip`)는
      `cw_i+cw_j<=W`인 블록쌍은 분리하지 않으므로, 그런 블록 3개 이상이
      동시에 bay 폭을 초과해도 MIP은 "충돌 없음"으로 본다. 이 위반을
      그대로 `_spatial`에 넘기면 대규모 postponement로 objective가
      폭증한다 (실측: prob_31 LNS+Gurobi 후보 `_objective` 583,584 →
      `check_feasibility` 300,901,137, bay1 동시점유 cw합 504 vs
      폭 37). `_repair_capacity`는 `_warm_start`/`_greedy_repair`와
      동일한 timeline 기반 용량 체크로 entry_time을 지연시켜 위반을
      해소한다 (이미 위반 없는 스케줄엔 no-op). 적용 지점:
      (1) `_adaptive_lns`의 candidate 평가 직전 — LNS의 accept/reject가
      실제 objective에 근접한 값을 보게 됨,
      (2) `algorithm()`의 `_finalize` — `_spatial` 직전에 적용해
      체크포인트 1/2 모두(워밍스타트·Phase1) 1D 용량 위반을 먼저 해소.
- [x] Phase 4: `_FAST_GREEDY_THRESHOLD` 재검토 — **버그 발견 및 수정**:
      값이 `1`로 설정되어 있어 `n >= _FAST_GREEDY_THRESHOLD`가 항상
      참이 되고, `algorithm()`이 Phase 0-1-2를 절대 실행하지 못한 채
      매번 `baseline_greedy`로 직행하고 있었다 (train 40문제 합산
      objective 32,007,280,742). Phase 2-0/2-1/2-2 이후 Phase 0-1-2가
      40/40 feasible(917M)을 달성했으므로, `_FAST_GREEDY_THRESHOLD`를
      `100_000`으로 올려 실질적으로 비활성화하고(`_checked_or_fallback`이
      안전망), `algorithm()`이 항상 Phase 0-1-2-`_spatial` 경로를
      타도록 수정 (iter3에서 train 40개 재검증 진행 중).

### 남은 작업 / 참고

- `algorithm()`에는 `_FAST_GREEDY_THRESHOLD`와 별개로 `timelimit <= 10`
  → `baseline_greedy` 폴백 분기가 있다. 프로덕션 기본값
  `timelimit=60`에서는 트리거되지 않으므로 이번 수정의 영향은 없지만,
  매우 짧은 timelimit으로 호출되는 경우라면 별도 검토가 필요하다.

### Gurobi 라이선스 조사 (참고)

- `grbgetkey`는 `apps.gurobi.com`/`packages.gurobi.com`/`www.gurobi.com`과
  통신해야 하는데, 이 샌드박스의 네트워크 정책이 모든 gurobi.com
  서브도메인을 차단(`host_not_allowed`)한다 — 이 환경에서는 라이선스 키
  활성화가 불가능하다.
- `pip install gurobipy`만으로 내장된 "Restricted license (non-production,
  2027-11-29 만료)"가 활성화 없이 오프라인으로 동작한다. prob_1(n=100,
  Gurobi MIP)·prob_26(n=150)·prob_31(n=200, LNS+Gurobi repair)에서
  `GurobiError`(라이선스 크기 제한) 없이 정상 동작 확인 — 모델 크기가
  제한 내에 들어옴.
- `ogc2026_env.yml`에 `gurobipy==13.0.2`가 명시되어 있어 production도
  `_HAS_GUROBI=True`일 가능성이 높다. 이 샌드박스의 Restricted
  license로 크래시가 없었으므로, production에서도 크래시 위험은 낮아
  보인다 (단, production의 실제 라이선스 종류는 확인 불가).
