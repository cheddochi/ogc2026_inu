#!/bin/bash
# OGC 2025 - 제출용 zip 패키지 생성 스크립트
# 사용법: bash build_submit.sh [출력파일명]
# 예시: bash build_submit.sh my_submission.zip

OUTPUT=${1:-"submission_$(date +%Y%m%d_%H%M%S).zip"}

echo "========================================"
echo " OGC 2025 제출 패키지 빌드"
echo "========================================"

# 필수 파일 존재 확인
REQUIRED=("myalgorithm.py" "util.py")
MISSING=0
for f in "${REQUIRED[@]}"; do
    if [ ! -f "$f" ]; then
        echo "❌ 필수 파일 없음: $f"
        MISSING=1
    fi
done

if [ $MISSING -eq 1 ]; then
    echo "빌드 중단: 필수 파일을 확인하세요."
    exit 1
fi

# 기존 zip 삭제
rm -f "$OUTPUT"

# myalgorithm.py를 최상위로, util.py 포함
# 추가 모듈이 있다면 modules/ 폴더로
zip "$OUTPUT" myalgorithm.py util.py

# modules/ 폴더가 있으면 포함
if [ -d "modules" ]; then
    zip -r "$OUTPUT" modules/
    echo "  modules/ 폴더 포함"
fi

# 모델 파일 폴더가 있으면 포함
if [ -d "models" ]; then
    zip -r "$OUTPUT" models/
    echo "  models/ 폴더 포함"
fi

echo ""
echo "✅ 패키지 생성 완료: $OUTPUT"
echo ""

# 구조 확인
echo "📦 압축 파일 구조:"
unzip -vl "$OUTPUT" | grep -v "^Archive\|^----\|files$" | awk '{print "  " $NF}'

echo ""

# myalgorithm.py 위치 검증
DEPTH=$(unzip -vl "$OUTPUT" | grep "myalgorithm.py" | awk '{print $NF}' | grep -c "/")
if [ "$DEPTH" -eq "0" ]; then
    echo "✅ myalgorithm.py 위치: 최상위 (OK)"
else
    echo "❌ myalgorithm.py 위치 오류: 하위 폴더에 있으면 안 됩니다!"
    exit 1
fi

# 파일 크기 확인
SIZE_MB=$(du -m "$OUTPUT" | cut -f1)
if [ "$SIZE_MB" -gt 30 ]; then
    echo "⚠️  파일 크기 ${SIZE_MB}MB 초과 (30MB 제한)"
else
    echo "✅ 파일 크기: ${SIZE_MB}MB (30MB 이하)"
fi
