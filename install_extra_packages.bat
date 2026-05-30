@echo off
REM OGC 2025 - 추가 패키지 설치 스크립트 (Windows)
REM conda activate ogc2025 이후 실행하세요

echo [1/8] torch_cluster 설치 중...
pip install torch_cluster==1.6.3 --find-links https://data.pyg.org/whl/torch-2.6.0+cu124.html

echo [2/8] torch-geometric 설치 중...
pip install torch_geometric==2.6.1

echo [3/8] torch_scatter 설치 중...
pip install torch_scatter==2.1.2 --find-links https://data.pyg.org/whl/torch-2.6.0+cu124.html

echo [4/8] torch_sparse 설치 중...
pip install torch_sparse==0.6.18 --find-links https://data.pyg.org/whl/torch-2.6.0+cu124.html

echo [5/8] torch_spline_conv 설치 중...
pip install torch_spline_conv==1.2.2 --find-links https://data.pyg.org/whl/torch-2.6.0+cu124.html

echo [6/8] cdlib 설치 중...
pip install cdlib==0.4.0

echo [7/8] leidenalg 설치 중...
pip install leidenalg==0.10.2

echo [8/8] stable_baselines3 설치 중...
pip install stable_baselines3==2.6.0

echo.
echo ✅ 추가 패키지 설치 완료!
pause
