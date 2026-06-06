#!/bin/bash
# OGC 2025 - 추가 패키지 설치 스크립트 (Linux/WSL/Mac)
# 사용법: conda activate ogc2025 후 bash install_extra_packages.sh

set -e  # 오류 발생 시 즉시 중단

# --- OS 감지 및 PyG 휠 URL 결정 ---
OS="$(uname -s)"
if [ "$OS" = "Darwin" ]; then
    echo "🍎 macOS 감지 → CPU 전용 휠 사용"
    PYG_URL="https://data.pyg.org/whl/torch-2.6.0+cpu.html"
    TORCH_EXTRA="+cpu"
else
    # Linux: CUDA 여부 확인
    if command -v nvidia-smi &> /dev/null; then
        echo "🐧 Linux + GPU 감지 → CUDA 12.4 휠 사용"
        PYG_URL="https://data.pyg.org/whl/torch-2.6.0+cu124.html"
        TORCH_EXTRA="+cu124"
    else
        echo "🐧 Linux CPU 감지 → CPU 전용 휠 사용"
        PYG_URL="https://data.pyg.org/whl/torch-2.6.0+cpu.html"
        TORCH_EXTRA="+cpu"
    fi
fi

# --- Step 0: torch 먼저 설치 (torch_cluster 빌드에 필요) ---
echo "[0/8] torch 설치 확인 중..."
if ! python -c "import torch" &> /dev/null; then
    echo "  torch 미설치 → 설치 시작..."
    pip install torch==2.6.0 torchvision==0.21.0 \
        --index-url "https://download.pytorch.org/whl${TORCH_EXTRA:+/$TORCH_EXTRA}"
else
    echo "  torch 이미 설치됨, 건너뜀"
fi

echo "[1/8] torch_cluster 설치 중..."
pip install torch_cluster --find-links "$PYG_URL"

echo "[2/8] torch-geometric 설치 중..."
pip install torch_geometric==2.6.1

echo "[3/8] torch_scatter 설치 중..."
pip install torch_scatter --find-links "$PYG_URL"

echo "[4/8] torch_sparse 설치 중..."
pip install torch_sparse --find-links "$PYG_URL"

echo "[5/8] torch_spline_conv 설치 중..."
pip install torch_spline_conv --find-links "$PYG_URL"

echo "[6/8] cdlib 설치 중..."
pip install cdlib==0.4.0

echo "[7/8] leidenalg 설치 중..."
pip install leidenalg==0.10.2

echo "[8/8] stable_baselines3 설치 중..."
pip install stable_baselines3==2.6.0

echo ""
echo "✅ 추가 패키지 설치 완료!"
