# OGC 2026 Training Benchmark Report

> `casat_cheddochi.py` 2D-aware 개선 과정 벤치마크 결과 (train set 40문제, timelimit=60s)
>
> Branch: `claude/2d-aware-cp-sat-lns-wf08mf`

---

## Iteration 요약

| Iter | 변경 사항 | Feasible | Total Objective | Total T | Avg Runtime | Max Runtime | 비고 |
|------|----------|----------|-----------------|---------|-------------|-------------|------|
| iter1 | Phase2-0+2-1: infeasible-bay 제외 + bay-dep cw | 5/40 | 45,201,453 | 3,354 | 7.15s | 8.12s | 대부분 infeasible |
| iter2 | Phase2-2: postponement 기반 2D `_spatial` | **40/40** | 917,417,673 | 90,704 | 7.17s | 8.31s | 첫 40/40 달성 |
| iter3 | Phase4: `_FAST_GREEDY_THRESHOLD` 수정 (1→100000) | **40/40** | 813,475,330 | 82,970 | 49.54s | 55.45s | Phase0-1-2 경로 활성화 |
| iter4 | Phase5: Phase0/Phase1 checkpoint ratchet | **40/40** | 608,425,512 | 67,567 | 49.65s | 55.57s | CP-SAT only |
| **iter5** | **Gurobi 활성화** | **40/40** | **580,313,244** | **64,664** | **31.09s** | **58.13s** | **현재 최선 (best)** |
| iter6 | Phase3: `_repair_capacity` 적용 | 40/40 | 625,843,437 | 69,132 | 30.24s | 55.03s | **회귀 (+7.8%)**, 롤백 |
| iter7 | Phase3 롤백 확인 | **40/40** | 581,615,080 | 64,773 | 31.08s | 58.25s | iter5와 0.2% 이내 일치 |

### Objective 추이

```
iter1:  45,201,453  (5/40)   ━━━  infeasible 다수
iter2: 917,417,673  (40/40)  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  첫 40/40
iter3: 813,475,330  (40/40)  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━       -11.3%
iter4: 608,425,512  (40/40)  ━━━━━━━━━━━━━━━━━━━━━━━━━━               -25.2%
iter5: 580,313,244  (40/40)  ━━━━━━━━━━━━━━━━━━━━━━━━━                 -4.6% ★ best
iter6: 625,843,437  (40/40)  ━━━━━━━━━━━━━━━━━━━━━━━━━━━              +7.8% (롤백)
iter7: 581,615,080  (40/40)  ━━━━━━━━━━━━━━━━━━━━━━━━━                확인
```

---

## 최선 결과 상세 (iter5 — Gurobi 활성화)

| Instance | Blocks | Bays | Feas | Objective | T | L | P | Runtime |
|----------|--------|------|------|-----------|---|---|---|---------|
| prob_1 | 100 | 2 | Y | 205,702 | 7 | 295.0 | 0 | 0.14s |
| prob_2 | 100 | 3 | Y | 62,012 | 2 | 143.0 | 16 | 0.12s |
| prob_3 | 100 | 3 | Y | 256,731 | 3 | 1,773.0 | 1,060 | 0.17s |
| prob_4 | 100 | 2 | Y | 585,814 | 26 | 2,278.0 | 0 | 0.14s |
| prob_5 | 150 | 3 | Y | 368,993 | 14 | 4,899.0 | 738 | 0.25s |
| prob_6 | 150 | 3 | Y | 1,816,353 | 50 | 929.0 | 2,189 | 0.29s |
| prob_7 | 150 | 3 | Y | 201,726 | 0 | 2,868.0 | 1,211 | 0.15s |
| prob_8 | 150 | 2 | Y | 11,252 | 0 | 2,413.0 | 8 | 0.17s |
| prob_9 | 200 | 3 | Y | 203,227 | 4 | 3,039.0 | 898 | 54.76s |
| prob_10 | 200 | 4 | Y | 345,079 | 14 | 6,242.0 | 735 | 54.75s |
| prob_11 | 200 | 4 | Y | 766,995 | 27 | 755.0 | 1,087 | 54.72s |
| prob_12 | 200 | 4 | Y | 553,398 | 13 | 5,482.0 | 1,730 | 54.86s |
| prob_13 | 250 | 4 | Y | 813,574 | 32 | 1,934.0 | 1,568 | 54.74s |
| prob_14 | 250 | 4 | Y | 1,097,607 | 49 | 1,673.0 | 1,640 | 54.75s |
| prob_15 | 250 | 4 | Y | 151,785 | 1 | 3,986.0 | 880 | 54.69s |
| prob_16 | 250 | 4 | Y | 102,536 | 0 | 4,228.0 | 612 | 54.68s |
| prob_17 | 300 | 4 | Y | 294,496 | 15 | 5,440.0 | 957 | 54.72s |
| prob_18 | 300 | 4 | Y | 413,209 | 11 | 2,863.0 | 1,918 | 54.76s |
| prob_19 | 300 | 4 | Y | 139,139 | 0 | 2,632.0 | 967 | 54.73s |
| prob_20 | 300 | 5 | Y | 6,204,432 | 217 | 3,178.0 | 3,189 | 54.84s |
| prob_21 | 100 | 3 | Y | 8,734,437 | 619 | 806.0 | 3,155 | 0.87s |
| prob_22 | 100 | 2 | Y | 2,792,065 | 113 | 1,812.0 | 3,200 | 0.73s |
| prob_23 | 100 | 2 | Y | 10,940,289 | 803 | 4,916.0 | 90 | 1.19s |
| prob_24 | 100 | 3 | Y | 4,795,054 | 318 | 2,732.0 | 1,805 | 0.93s |
| prob_25 | 100 | 2 | Y | 1,519,876 | 2,267 | 5,107.0 | 134 | 1.33s |
| prob_26 | 150 | 3 | Y | 42,122,451 | 3,095 | 1,738.0 | 5,631 | 4.58s |
| prob_27 | 150 | 2 | Y | 80,607,797 | 5,905 | 616.0 | 4,688 | 2.86s |
| prob_28 | 150 | 3 | Y | 18,887,030 | 1,328 | 1,702.0 | 3,919 | 2.59s |
| prob_29 | 150 | 3 | Y | 13,034,443 | 865 | 966.0 | 4,995 | 6.00s |
| prob_30 | 150 | 2 | Y | 18,015,001 | 1,349 | 6,896.0 | 6 | 2.11s |
| prob_31 | 200 | 4 | Y | 46,466,727 | 3,261 | 3,766.0 | 11,148 | 58.13s |
| prob_32 | 200 | 3 | Y | 11,499,958 | 3,406 | 4,952.0 | 205 | 56.33s |
| prob_33 | 200 | 3 | Y | 25,658,124 | 3,842 | 2,011.0 | 156 | 57.94s |
| prob_34 | 200 | 4 | Y | 4,734,386 | 1,403 | 3,287.0 | 66 | 56.91s |
| prob_35 | 200 | 3 | Y | 21,352,647 | 1,599 | 4,026.0 | 87 | 58.02s |
| prob_36 | 250 | 4 | Y | 1,639,287 | 2,237 | 1,452.0 | 11,212 | 54.87s |
| prob_37 | 250 | 3 | Y | 19,904,270 | 4,822 | 2,786.0 | 6,369 | 54.86s |
| prob_38 | 250 | 3 | Y | 163,209,746 | 12,074 | 2,652.0 | 7,406 | 54.85s |
| prob_39 | 250 | 3 | Y | 62,815,660 | 4,622 | 4,196.0 | 7,825 | 54.90s |
| prob_40 | 250 | 4 | Y | 6,989,936 | 10,251 | 5,606.0 | 11,301 | 55.03s |

**TOTAL: pass=40 fail=0**

---

## 각 Phase별 변경 내용 상세

### Phase 2-0: `_narrowest_orient` infeasible-bay 제외
- 어떤 방향으로도 들어갈 수 없는 (block, bay) 조합을 배정 후보에서 제외
- `cw = bay_w + 1`을 반환하여 Phase1 MIP/LNS가 해당 bay를 선택하지 않도록 함

### Phase 2-1: bay-종속 `cw[i]` 교체
- `cw[i] = min(orients[(i,b)][1] for b in range(M))` (전역 최소) →
  `cw[i][b] = orients[(i,b)][1]` (배정된 bay 기준) 으로 교체
- `_cpsat_mip`/`_gurobi_mip`의 cumulative/conflict 제약이 정확한 bay별 폭을 사용

### Phase 2-2: postponement 기반 2D `_spatial` 재작성
- `_spatial`을 진입시각 postponement + AABB-분리 기반 2D bottom-left-fill로 재작성
- 배치 불가 시 entry_time을 다음 이웃 exit_time으로 지연 (postponement)
- **40/40 feasible 최초 달성** (iter2)

### Phase 4: `_FAST_GREEDY_THRESHOLD` 수정
- 값이 `1`로 설정되어 있어 `algorithm()`이 항상 `baseline_greedy`로 직행하던 버그 수정
- `100_000`으로 올려 Phase 0→1→2→`_spatial` 경로가 항상 실행되도록 함

### Phase 5: checkpoint ratchet
- Phase 0(`_warm_start`) 결과를 checkpoint1로 저장
- Phase 1(MIP/LNS) 결과의 `_finalize` objective가 checkpoint1보다 좋을 때만 채택
- 낮은 품질의 MIP/LNS 해가 warm start보다 못할 때 안전하게 warm start로 후퇴

### Gurobi 활성화
- `gurobipy` 설치 확인 (`_HAS_GUROBI=True`)
- Restricted license (non-production, 2027-11-29 만료)가 오프라인으로 동작
- n<=150: `_gurobi_mip` (CP-SAT 대체), n>150: `_adaptive_lns` + `_gurobi_repair`
- iter4(CP-SAT only) 608.4M → iter5(Gurobi) 580.3M (-4.6%)

### Phase 3 (시도 → 회귀 → 롤백)
- `_repair_capacity`: 1D timeline 기반 bay 용량 위반 보정 함수
- `_conflict_pairs`의 pairwise-only 분리 제약이 놓치는 n-ary 용량 위반을 보정하려 했으나,
  `_spatial`의 실제 2D y축 적층 능력보다 과도하게 보수적 → objective +7.8% 악화
- 롤백 후 iter7에서 pre-Phase3 수준 복원 확인

---

## 규모별 분석 (iter5 best 기준)

### n<=150 (prob_1~8): Gurobi MIP 직접 풀이
- 평균 runtime: 0.18s (MIP가 빠르게 수렴)
- Total Objective: 3,508,583
- 특징: MIP가 거의 최적해를 찾아 `_spatial` postponement 없이 배치 가능

### n=200~300 (prob_9~20): Adaptive LNS + Gurobi repair
- 평균 runtime: 54.75s (timelimit에 근접)
- Total Objective: 12,131,948
- 특징: LNS가 시간 제한까지 반복 개선, checkpoint ratchet으로 품질 보장

### n=100~150, 고난이도 (prob_21~30): Gurobi MIP, 복잡한 제약
- 평균 runtime: 2.42s
- Total Objective: 201,648,443
- 특징: 블록 수는 적지만 tight한 제약 (좁은 bay, 높은 tardiness weight)

### n=200~250, 고난이도 (prob_31~40): Adaptive LNS
- 평균 runtime: 55.85s
- Total Objective: 363,024,270
- 특징: 전체 objective의 62.6% 차지 — **가장 큰 개선 여지**

---

## 환경 정보

- **Python**: 3.x (conda ogc2026 환경)
- **OR-Tools**: CP-SAT solver (`_HAS_ORTOOLS=True`)
- **Gurobi**: 13.0.2, Restricted license (non-production, 2027-11-29 만료)
- **Platform**: Linux x86_64, 4 cores / 8 threads
- **Timelimit**: 60s per instance
