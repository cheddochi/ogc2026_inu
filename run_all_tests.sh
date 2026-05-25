#!/bin/bash
# OGC 2025 - 전체 사이즈 일괄 테스트
# 사용법: bash run_all_tests.sh [timelimit]

TIMELIMIT=${1:-60}
SIZES=("tiny" "small" "medium" "large")

echo "========================================"
echo " OGC 2025 전체 사이즈 일괄 테스트"
echo " 제한 시간: ${TIMELIMIT}초 / 사이즈: ${SIZES[*]}"
echo "========================================"
echo ""

PASS=0
FAIL=0

for SIZE in "${SIZES[@]}"; do
    PROB_FILE="problem_${SIZE}.json"

    # 문제 파일 생성
    if [ ! -f "$PROB_FILE" ]; then
        python problem_generator.py --size "$SIZE" --out "$PROB_FILE" > /dev/null 2>&1
    fi

    # 결과 파일 분리 저장
    RESULT_FILE="results_${SIZE}.json"

    # 실행
    START=$(date +%s%N)
    python myalgorithm.py "$SIZE" "$PROB_FILE" "$TIMELIMIT" > /dev/null 2>&1
    EXIT=$?
    END=$(date +%s%N)
    ELAPSED=$(( (END - START) / 1000000 ))

    if [ $EXIT -eq 0 ] && [ -f results.json ]; then
        cp results.json "$RESULT_FILE"
        RESULT=$(python -c "
import json
with open('results.json') as f:
    r = json.load(f)
feasible = r['feasible']
obj = r.get('obj', 'N/A')
t = r.get('time', 0)
print(f'feasible={feasible}  obj={obj}  time={t:.2f}s')
")
        echo "  [$SIZE] ✅ $RESULT"
        PASS=$((PASS + 1))
    else
        echo "  [$SIZE] ❌ 실패 (exit=$EXIT, ${ELAPSED}ms)"
        FAIL=$((FAIL + 1))
    fi
done

echo ""
echo "========================================"
echo " 결과: ${PASS}개 성공 / ${FAIL}개 실패"
echo "========================================"
