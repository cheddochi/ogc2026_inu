#!/bin/bash
# OGC 2025 - 로컬 테스트 실행 스크립트
# 사용법: bash run_test.sh [문제크기] [timelimit]
#   문제크기: tiny / small / medium / large (기본: small)
#   timelimit: 초 단위 (기본: 60)
#
# 예시:
#   bash run_test.sh               # small 문제, 60초
#   bash run_test.sh medium 120    # medium 문제, 120초

SIZE=${1:-small}
TIMELIMIT=${2:-60}
PROB_FILE="problem_${SIZE}.json"

echo "========================================"
echo " OGC 2025 로컬 테스트"
echo " 문제 크기: $SIZE / 제한 시간: ${TIMELIMIT}초"
echo "========================================"

# 1. 문제 파일 없으면 생성
if [ ! -f "$PROB_FILE" ]; then
    echo "[1/2] 문제 파일 생성 중: $PROB_FILE"
    python problem_generator.py --size "$SIZE" --out "$PROB_FILE"
else
    echo "[1/2] 기존 문제 파일 사용: $PROB_FILE"
fi

# 2. 알고리즘 실행
echo "[2/2] 알고리즘 실행 중..."
python myalgorithm.py "$SIZE" "$PROB_FILE" "$TIMELIMIT"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 완료! 결과 확인: results.json"
    echo ""
    # 결과 요약 출력
    python -c "
import json
with open('results.json') as f:
    r = json.load(f)
print(f'  feasible : {r[\"feasible\"]}')
print(f'  obj      : {r.get(\"obj\", \"N/A\")}')
print(f'  time     : {r.get(\"time\", 0):.2f}초')
if r.get('infeasibility'):
    print(f'  오류     : {r[\"infeasibility\"][:3]}')
"
elif [ $EXIT_CODE -eq 1 ]; then
    echo "❌ 알고리즘 실행 중 예외 발생 (exit code 1)"
else
    echo "⚠️  사용법 오류 (exit code 2)"
fi
