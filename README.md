# OGC 2025 - 개발환경 가이드 (Windows PowerShell)

> 🪟 **이 문서는 Windows + PowerShell 환경 기준입니다.**  
> macOS Apple Silicon 환경은 `README_macOS.md`를 참고하세요.

## 📋 목차
- [Update History](#update-history)
- [1. 환경설정](#1-환경설정)
- [2. 알고리즘 제출 방법](#2-알고리즘-제출-방법)
- [3. alg_tester 사용법](#3-alg_tester-사용법)
- [4. 로컬 테스트 환경 (커스텀)](#4-로컬-테스트-환경-커스텀)

---

## Update History

| 날짜 | 내용 |
|------|------|
| 2025/07/19 | `baseline_20250719` 업데이트 (heuristics 버그 수정) |
| 2025/07/05 | `baseline_20250705` 업데이트 (`util.py` 버그 수정) |
| 2025/06/01 | `baseline_20250601` 업데이트 (heuristics 버그 수정) |
| 2025/05/31 | `baseline_20250531` 업데이트 (minor 버그 수정) |
| 2025/05/19 | `baseline_20250519` 업데이트 (minor 버그 수정) |
| 2025/05/07 | 페이지 최초 작성 |

---

## 1. 환경설정

알고리즘 제출 전, 개인 PC에서 평가 서버와 동일한 Python 환경을 구성해야 합니다.

### 사용 가능한 Python 패키지

| 패키지 | 버전 |
|--------|------|
| python | 3.11 |
| jupyterlab | 4.4.1 |
| notebook | 7.4.1 |
| ipympl | 0.9.7 |
| matplotlib | 3.8.4 |
| pandas | 2.2.3 |
| networkx | 3.4.2 |
| scipy | 1.15.2 |
| scikit-learn | 1.6.1 |
| numba | 0.61.0 |
| cython | 3.0.10 |
| jsbeautifier | - |
| ortools | 9.11.4210 |
| gurobipy | 12.0.1 |
| xpress | 9.5.4 |
| gymnasium | 1.1.1 |
| torch | 2.6.0 |
| torchvision | 0.21.0 |
| tensorflow | 2.18.0 |
| keras | 3.9.0 |

> 💡 필요한 패키지가 목록에 없으면 Slack 채널에서 요청하세요.

**numpy**
파이썬 수치 계산의 기반 라이브러리입니다. 다차원 배열(ndarray)을 C 수준 속도로 처리하며, pandas/shapely/OR-Tools 모두 내부적으로 numpy에 의존합니다.

```python
import numpy as np

a = np.array([1, 2, 3])
np.zeros((3, 4))       # 3×4 영행렬
np.mean(a)             # 평균
np.argmin(a)           # 최솟값 인덱스
```

---

**OGC에서의 활용**

베이스라인 코드에서도 이미 핵심적으로 쓰이고 있습니다.

```python
# 노드 할당 상태 관리
node_allocations = np.ones(N, dtype=int) * -1

# 최단 거리 배열
shortest_distances = np.zeros(N, dtype=int)

# 경로를 indicator 벡터로 변환
path_array = np.zeros(N, dtype=int)
path_array[path[:-1]] = 1
```

리스트 대신 numpy 배열을 쓰면 노드 수가 커질수록 연산 속도 차이가 크게 납니다. 알고리즘 개선 시 거리 행렬이나 비용 계산 부분을 numpy로 벡터화하면 성능 향상에 효과적입니다.

세 라이브러리 모두 최적화/물류 분야에서 자주 함께 쓰입니다.

---

**pandas**
표 형태 데이터를 다루는 기본 라이브러리입니다. DataFrame 구조로 CSV, Excel, JSON 등을 읽고 필터링, 집계, 병합, 결측치 처리 등을 SQL처럼 다룰 수 있습니다. OGC 문제에서는 수요 데이터나 노드 정보를 전처리할 때 유용합니다.

```python
import pandas as pd
df = pd.read_csv('demands.csv')
df[df['quantity'] > 2]  # 수량 2 초과 필터링
```

---

**shapely**
2D 기하학 객체(점, 선, 다각형)를 다루는 라이브러리입니다. 좌표 기반으로 거리 계산, 교차 여부, 포함 관계 등을 처리합니다. 물류에서는 서비스 구역 설정, 경로의 공간적 분석, 지도 기반 최적화에 활용됩니다.

```python
from shapely.geometry import Point, Polygon
zone = Polygon([(0,0), (4,0), (4,4), (0,4)])
p = Point(2, 2)
p.within(zone)  # True
```

---

**OR-Tools**
Google이 만든 조합 최적화 라이브러리입니다. VRP(차량 경로 문제), TSP(외판원 문제), 스케줄링, 정수 계획법 등을 풀 수 있습니다. OGC처럼 항구 경로 최적화 문제에 직접 적용 가능한 도구입니다.

```python
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
# VRP 솔버 설정 후 최적 경로 탐색
```

---

**세 라이브러리의 관계**

OGC 문제 기준으로 보면 pandas로 입력 데이터를 정제하고, shapely로 노드 간 공간 관계를 분석하고, OR-Tools로 최적 경로를 탐색하는 흐름으로 연결됩니다. 특히 OR-Tools는 베이스라인의 휴리스틱을 대체하거나 보완하는 용도로 바로 활용할 수 있어 OGC에서 가장 주목할 라이브러리입니다.


### 추가 설치 패키지 (요청 반영)

| 패키지 | 버전 | Windows 설치 비고 |
|--------|------|-------------------|
| torch_cluster | 1.6.3+pt26cu124 | GPU 있으면 CUDA 12.4 휠, 없으면 CPU 휠 |
| torch-geometric | 2.6.1 | 동일 |
| torch_scatter | 2.1.2+pt26cu124 | GPU 있으면 CUDA 12.4 휠, 없으면 CPU 휠 |
| torch_sparse | 0.6.18+pt26cu124 | GPU 있으면 CUDA 12.4 휠, 없으면 CPU 휠 |
| torch_spline_conv | 1.2.2+pt26cu124 | GPU 있으면 CUDA 12.4 휄, 없으면 CPU 휠 |
| cdlib | 0.4.0 | 동일 |
| leidenalg | 0.10.2 | 동일 |
| stable_baselines3 | 2.6.0 | 동일 |

---

### Conda 환경 설정

Windows에는 **Miniforge** 사용을 권장합니다.

#### 1단계. Miniforge 설치

[https://github.com/conda-forge/miniforge](https://github.com/conda-forge/miniforge) 에서  
`Miniforge3-Windows-x86_64.exe` 다운로드 후 설치합니다.

> 💡 설치 후 시작 메뉴에서 **Miniforge Prompt** 또는 **Anaconda Prompt**를 사용하세요.  
> 일반 PowerShell에서 conda를 사용하려면 아래 명령어로 초기화가 필요합니다.

```powershell
# PowerShell에서 conda 활성화 초기화 (최초 1회)
conda init powershell

# 이후 PowerShell 재시작
```

> ⚠️ PowerShell 실행 정책 오류 발생 시 (스크립트 실행 차단):
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

#### 2단계. 환경 생성

`ogc2025_env_20250506.yml.zip`을 다운로드하고 압축 해제 후 실행합니다.

```powershell
# yml 파일이 있는 폴더로 이동
cd C:\Users\사용자명\Downloads

# 환경 생성
conda env create -f ogc2025_env_20250506.yml
```

> 💡 torch, tensorflow 설치 오류 시 해당 항목을 yml에서 삭제 후 아래와 같이 별도 설치하세요.

```powershell
# GPU 없는 경우 (CPU 전용)
pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cpu

# NVIDIA GPU가 있는 경우 (CUDA 12.4)
pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu124
```

#### 3단계. 환경 활성화

```powershell
conda activate ogc2025
```

터미널 프롬프트에 `(ogc2025)`가 표시되면 완료입니다.

***4단계.** Gurobi for Python 설치
```bash
conda install -c gurobi gurobi
```


---

## 2. 알고리즘 제출 방법

### 필요 파일 다운로드

```
baseline_20250719.zip          ← 알고리즘 예제 코드
exercise_problems_20250512.zip ← 연습 문제
```

```powershell
# PowerShell에서 압축 해제
Expand-Archive -Path baseline_20250719.zip -DestinationPath .
Expand-Archive -Path exercise_problems_20250512.zip -DestinationPath .

# 파일 목록 확인 (prob1.json ~ prob10.json 형식)
Get-ChildItem exercise_problems\
```

---

### 베이스라인 파일 구조

```
baseline\
├── myalgorithm.py   ← 알고리즘 구현 파일 (가장 중요!)
└── util.py          ← 알고리즘 구현 보조 함수 모음
```

---

### myalgorithm.py 작성 방법

```python
def algorithm(prob_info, timelimit=60):
    #------------- begin of custom algorithm code --------------#
    
    # 여기에 알고리즘 코드를 작성하세요
    
    #------------- end of custom algorithm code --------------#
    return solution
```

> ⚠️ `myalgorithm.py` 파일명과 `def algorithm(prob_info, timelimit=60):` 함수 시그니처는 **절대 변경 불가**합니다.

---

### prob_info 데이터 구조

```python
N = prob_info['N']  # 노드 수 (0: gate 노드, 1~N-1: 차량 적재 가능 노드)
E = prob_info['E']  # Edge list (undirected)
K = prob_info['K']  # 수요 list: [ [[o, d], quantity], ... ]
P = prob_info['P']  # 항구 수 (0 ~ P-1 순서로 방문)
F = prob_info['F']  # 경로 고정비
```

---

### 해(solution) 형식

```python
solution = {
    0: [
        [[0, 1, 3, 5, 6, 9, 15, 20, 22], 2],
        ...
    ],
    1: [
        [[9, 6, 5, 3, 1, 0], 0],
        ...
    ]
}
```

---

### 해 유효성 검증

```python
result = check_feasibility(prob_info, solution)
# {'obj': 588.0, 'feasible': True, 'infeasibility': None}
```

---

### 제출 규칙

- **형식**: `.zip` 파일 (파일명 자유)
- **필수 파일**: `myalgorithm.py`, `util.py`
- `myalgorithm.py`는 **압축 파일 최상위**에 위치해야 함
- `util.py` 수정 불가
- **최대 파일 크기**: 30MB

```powershell
# 압축 파일 내부 구조 확인 (PowerShell)
[System.IO.Compression.ZipFile]::OpenRead("submission.zip").Entries | Select-Object FullName
```

---

### 에러 코드 안내

| 에러 코드 | 설명 |
|-----------|------|
| `infeasible` | 도출한 해가 유효하지 않음 |
| `time_limit` | 실행 시간이 제한을 초과함 |
| `crash` | 비정상 종료 (segmentation fault) |
| `algo_error` | 알고리즘 내부 에러 발생 |
| `test_error(01)` | 압축 파일 해제 실패 (잘못된 형식) |
| `test_error(02)` | 최상위 폴더에 `myalgorithm.py` 없음 |
| `test_error(03)` | `ogc2025` 환경에 없는 패키지 import 시도 |
| `sys_error` | 평가 시스템 에러 |

---

### Python 외 언어 사용

- 필요한 라이브러리를 **모두 압축 파일에 포함**하여 제출
- 평가 서버 환경: **Linux/Ubuntu 24.04**

> ⚠️ Windows에서 빌드한 `.exe` 바이너리는 평가 서버(Linux)에서 실행되지 않습니다.  
> C/C++ 등을 사용하는 경우 WSL2(Ubuntu 24.04) 또는 Docker에서 빌드하세요.

---

## 3. alg_tester 사용법

```powershell
# ogc2025 환경 활성화 후
conda activate ogc2025
jupyter lab
```

`alg_tester.ipynb` 파일을 열고 첫 번째 셀을 실행(`Ctrl + Enter`)합니다.

> ⚠️ `alg_tester`에서 정상 동작해도 평가 서버 환경 차이로 오류가 발생할 수 있습니다.  
> 최종 검증은 WSL2(Ubuntu 24.04) 또는 Docker 환경에서 진행하세요.

---

## 4. 로컬 테스트 환경 (커스텀)

공식 `alg_tester` 외에 PowerShell에서 바로 실행·검증·제출 패키지 빌드까지 가능한 커스텀 스크립트 셋입니다.

### 4-1. 프로젝트 파일 구조

```
ogc2025\
├── myalgorithm.py                ← 알고리즘 구현 (수정 대상)
├── util.py                       ← 유틸 함수 (수정 불가)
├── problem_generator.py          ← 테스트용 샘플 문제 생성기
├── requirements.txt              ← pip 의존 패키지 목록
├── install_extra_packages.bat    ← 추가 PyG 계열 패키지 설치 (Windows)
└── exercise_problems\            ← 공식 연습 문제 폴더
```

> ℹ️ Windows에서는 `.sh` 스크립트를 직접 실행할 수 없습니다.  
> 아래 섹션의 PowerShell 명령어를 직접 사용하거나, WSL2를 설치하면 `.sh` 스크립트도 사용 가능합니다.

---

### 4-2. 환경 설치

```powershell
# conda 환경 생성 및 활성화
conda env create -f ogc2025_env_20250506.yml
conda activate ogc2025

# 핵심 패키지 설치
pip install -r requirements.txt

# 추가 패키지 설치 (PyG 계열, 필요 시)
.\install_extra_packages.bat
```

---

### 4-3. 테스트 실행

#### 공식 연습 문제로 직접 실행

```powershell
# 연습 문제 압축 해제
Expand-Archive -Path exercise_problems_20250512.zip -DestinationPath .

# 파일명은 prob1.json ~ prob10.json (prob_01 아님에 주의)
python myalgorithm.py prob1 exercise_problems\prob1.json 60
```

#### 샘플 문제로 테스트

공식 연습 문제가 없는 경우 샘플 문제를 생성해서 테스트합니다.

```powershell
# 문제 생성
python problem_generator.py --size small

# 알고리즘 실행 (60초 제한)
python myalgorithm.py test_small problem_small.json 60
```

#### 전체 사이즈 일괄 테스트 (PowerShell)

```powershell
# PowerShell에서 직접 일괄 실행
foreach ($size in @("tiny", "small", "medium", "large")) {
    $prob = "problem_$size.json"

    # 문제 파일 없으면 생성
    if (-not (Test-Path $prob)) {
        python problem_generator.py --size $size --out $prob
    }

    # 알고리즘 실행
    python myalgorithm.py $size $prob 60

    # 결과 출력
    if (Test-Path results.json) {
        $r = Get-Content results.json | ConvertFrom-Json
        Write-Host "[$size] feasible=$($r.feasible)  obj=$($r.obj)  time=$([math]::Round($r.time,2))s"
        Copy-Item results.json "results_$size.json"
    }
}
```

실행 결과 예시:
```
[tiny]   feasible=True  obj=2.0   time=0.00s
[small]  feasible=True  obj=24.0  time=0.00s
[medium] feasible=True  obj=68.0  time=0.01s
[large]  feasible=True  obj=142.0 time=0.03s
```

---

### 4-4. 샘플 문제 생성기

```powershell
python problem_generator.py                              # small (기본)
python problem_generator.py --size tiny                  # tiny
python problem_generator.py --size large                 # large
python problem_generator.py --size medium --seed 123 --out my_prob.json
```

| 사이즈 | 노드 수 | 항구 수 | 특징 |
|--------|---------|---------|------|
| tiny   | 7       | 2       | 동작 확인용 |
| small  | 13      | 3       | 기본 테스트 |
| medium | 25      | 4       | 중간 규모 |
| large  | 41      | 5       | 성능 테스트 |

---

### 4-5. 제출 패키지 빌드 (PowerShell)

```powershell
# 기존 zip 삭제 후 재생성
$output = "submission_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
Remove-Item $output -ErrorAction SilentlyContinue

Compress-Archive -Path myalgorithm.py, util.py -DestinationPath $output

# modules 폴더가 있으면 포함
if (Test-Path modules) {
    Compress-Archive -Path modules -Update -DestinationPath $output
}

Write-Host "✅ 패키지 생성 완료: $output"

# 구조 확인
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($output)
$zip.Entries | ForEach-Object { Write-Host "  $($_.FullName)" }
$zip.Dispose()

# myalgorithm.py 최상위 위치 검증
$isTopLevel = $zip.Entries | Where-Object { $_.FullName -eq "myalgorithm.py" }
if ($isTopLevel) {
    Write-Host "✅ myalgorithm.py 위치: 최상위 (OK)"
} else {
    Write-Host "❌ myalgorithm.py가 최상위에 없습니다. 구조를 확인하세요."
}
```

---

### 4-6. 결과 확인

```powershell
# 결과 파일 읽기
Get-Content results.json

# 또는 파싱해서 요약 출력
$r = Get-Content results.json | ConvertFrom-Json
Write-Host "feasible : $($r.feasible)"
Write-Host "obj      : $($r.obj)"
Write-Host "time     : $([math]::Round($r.time, 4))s"
```

```json
{
  "feasible": true,
  "obj": 24.0,
  "infeasibility": null,
  "time": 0.0029,
  "timelimit_exception": false,
  "prob_name": "prob1",
  "prob_file": "exercise_problems\\prob1.json"
}
```

| 필드 | 설명 |
|------|------|
| `feasible` | 해 유효 여부 |
| `obj` | 목적 함수값 (총 경로 비용 - LB, **낮을수록 좋음**) |
| `infeasibility` | 유효하지 않을 경우 사유 목록 |
| `time` | 실제 실행 시간(초) |
| `timelimit_exception` | 제한 시간 초과 여부 |

---

## 📌 빠른 시작 체크리스트 (Windows)

```
[ ] Miniforge 설치 (Miniforge3-Windows-x86_64.exe)
[ ] PowerShell 실행 정책 설정: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
[ ] conda init powershell 실행 후 PowerShell 재시작
[ ] conda env create -f ogc2025_env_20250506.yml
[ ] conda activate ogc2025
[ ] pip install -r requirements.txt
[ ] baseline_20250719.zip 및 exercise_problems_20250512.zip 다운로드
[ ] Expand-Archive로 압축 해제  →  파일명: prob1.json ~ prob10.json
[ ] myalgorithm.py에 알고리즘 작성
[ ] python myalgorithm.py prob1 exercise_problems\prob1.json 60 으로 단일 테스트
[ ] PowerShell 일괄 테스트 스크립트로 전체 사이즈 검증
[ ] check_feasibility()로 해 유효성 최종 확인
[ ] Compress-Archive로 제출 패키지 빌드 및 구조 검증
[ ] alg_tester로 제출 형식 최종 검증
[ ] 제출
```


# Gurobi Named-User Academic 라이선스 설치 가이드

> 🎓 **이 문서는 Gurobi Named-User Academic 라이선스를 발급받고**  
> **Windows PowerShell / macOS Apple Silicon 환경에 설치하는 방법을 설명합니다.**

## 📋 목차
- [1. 라이선스 발급](#1-라이선스-발급)
- [2. Gurobi 설치](#2-gurobi-설치)
  - [Windows PowerShell](#windows-powershell)
  - [macOS Apple Silicon](#macos-apple-silicon)
- [3. 라이선스 활성화](#3-라이선스-활성화)
- [4. 환경변수 설정](#4-환경변수-설정)
- [5. conda 환경에 gurobipy 설치](#5-conda-환경에-gurobipy-설치)
- [6. 설치 확인](#6-설치-확인)
- [7. 트러블슈팅](#7-트러블슈팅)

---

## 1. 라이선스 발급

### 1-1. Gurobi 계정 등록

1. [https://portal.gurobi.com/iam/register](https://portal.gurobi.com/iam/register) 접속
2. **Academic** 선택 후 **대학 이메일**로 가입 (일반 Gmail 등은 불가)
3. 가입 후 이메일 인증 완료

### 1-2. Named-User Academic 라이선스 생성

1. [https://portal.gurobi.com](https://portal.gurobi.com) 로그인
2. 상단 메뉴 **Licenses** 클릭
3. **Request** → **GENERATE NOW** (Named-User Academic 블록) 클릭
4. 라이선스가 생성되면 목록에 표시됨

> ⚠️ **라이선스 유효기간**: 최대 1년, 갱신 가능 (학적 유지 시)  
> ⚠️ **Named-User 라이선스는 1인 1대 전용**입니다. 다른 PC에서 사용하려면 별도 라이선스를 발급받아야 합니다.

### 1-3. grbgetkey 명령어 확인

1. 라이선스 목록에서 해당 라이선스의 **설치 아이콘** 클릭
2. 팝업에서 아래와 같은 명령어 복사:
   ```
   grbgetkey xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ```

> 💡 이 키는 이후 라이선스 활성화 단계에서 사용합니다.

---

## 2. Gurobi 설치

### Windows PowerShell

#### 방법 A — conda로 설치 (권장)

```powershell
# ogc2025 환경 활성화
conda activate ogc2025

# Gurobi conda 채널에서 설치
conda install -c gurobi gurobi
```

#### 방법 B — pip으로 설치

```powershell
conda activate ogc2025
pip install gurobipy
```

> ⚠️ pip 설치 시 `grbgetkey` 등 라이선스 도구가 포함되지 않습니다.  
> 라이선스 활성화를 위해 **방법 A (conda)** 를 권장합니다.

---

### macOS Apple Silicon

#### 방법 A — conda로 설치 (권장)

```bash
# ogc2025 환경 활성화
conda activate ogc2025

# Gurobi conda 채널에서 설치 (Apple Silicon arm64 자동 감지)
conda install -c gurobi gurobi
```

#### 방법 B — pip으로 설치

```bash
conda activate ogc2025
pip install gurobipy
```

> 💡 Gurobi 9.1 이후 버전은 Apple Silicon(arm64) 네이티브를 지원합니다.  
> conda 설치 시 `macos_universal2` 패키지가 자동으로 선택됩니다.

---

## 3. 라이선스 활성화

> ⚠️ **활성화 시 대학 네트워크 필수** — 교내 Wi-Fi에 직접 연결하거나, 대학 VPN을 통해 연결해야 합니다.  
> 활성화 완료 후에는 인터넷 연결 없이도 사용 가능합니다.

### Windows PowerShell

```powershell
# conda 환경 활성화 상태에서 실행
conda activate ogc2025

# 라이선스 키로 활성화 (1-3에서 복사한 키 사용)
grbgetkey xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

라이선스 파일 저장 경로를 묻는 프롬프트가 나오면 **Enter**로 기본값 사용:
```
Enter the path in which to store the Gurobi license key file
[default: C:\Users\사용자명]:
```

기본 저장 경로: `C:\Users\사용자명\gurobi.lic`

---

### macOS Apple Silicon

```bash
# conda 환경 활성화 상태에서 실행
conda activate ogc2025

# 라이선스 키로 활성화
grbgetkey xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

라이선스 파일 저장 경로를 묻는 프롬프트:
```
Enter the path in which to store the Gurobi license key file
[default: /Users/사용자명]:
```

**Enter**로 기본값 사용하거나 원하는 경로 입력:
```bash
# 예: 별도 폴더에 저장하는 경우
/Users/dohunkwon/Workspace/gurobi_lic
```

기본 저장 경로: `/Users/사용자명/gurobi.lic`

---

## 4. 환경변수 설정

라이선스 파일을 기본 경로(홈 디렉토리)가 아닌 **별도 경로에 저장**한 경우에만 설정이 필요합니다.

### Windows PowerShell

**영구 설정 (시스템 환경변수):**

1. 시작 메뉴 → **환경 변수 편집** 검색 → 실행
2. **시스템 변수** → **새로 만들기**
3. 변수 이름: `GRB_LICENSE_FILE`
4. 변수 값: `C:\Users\사용자명\gurobi_lic\gurobi.lic`
5. 확인 → PowerShell 재시작

**또는 PowerShell에서 영구 설정:**
```powershell
[System.Environment]::SetEnvironmentVariable(
    "GRB_LICENSE_FILE",
    "C:\Users\사용자명\gurobi_lic\gurobi.lic",
    "User"
)
```

**conda 환경에만 적용:**
```powershell
conda activate ogc2025
conda env config vars set GRB_LICENSE_FILE=C:\Users\사용자명\gurobi_lic\gurobi.lic
conda activate ogc2025  # 재활성화 후 적용
```

---

### macOS Apple Silicon

**영구 설정 (~/.zshrc):**
```bash
echo 'export GRB_LICENSE_FILE=/Users/dohunkwon/Workspace/gurobi_lic/gurobi.lic' >> ~/.zshrc
source ~/.zshrc
```

**conda 환경에만 적용 (권장):**
```bash
conda activate ogc2025
conda env config vars set GRB_LICENSE_FILE=/Users/dohunkwon/Workspace/gurobi_lic/gurobi.lic
conda activate ogc2025  # 재활성화 후 적용
```

---

## 5. conda 환경에 gurobipy 설치

OGC 환경에서 gurobipy를 사용하려면 conda 환경에 추가 설치가 필요합니다.

```bash
# Windows / macOS 공통
conda activate ogc2025
conda install -c gurobi gurobi

# 또는 pip
pip install gurobipy==11.0.0  # OGC 서버 버전(12.0.1)과 다를 수 있음
```

> 💡 OGC 평가 서버는 `gurobipy==12.0.1`을 사용합니다.  
> 로컬에서 버전 불일치가 있어도 기본 동작에는 문제없으나, 정확한 재현을 원하면 버전을 맞추세요:
> ```bash
> pip install gurobipy==12.0.1
> ```

---

## 6. 설치 확인

### Python에서 확인

```python
import gurobipy as gp

m = gp.Model()
print("Gurobi 설치 확인 완료!")
```

정상 출력 예시:
```
Set parameter Username
Set parameter LicenseID to value 2829206
Academic license - for non-commercial use only - expires 2026-XX-XX
Gurobi 설치 확인 완료!
```

### CLI에서 확인

```bash
# Windows
gurobi_cl --version

# macOS
gurobi_cl --version
```

출력 예시:
```
Gurobi Optimizer version 13.0.1 build v13.0.1rc1 (mac64[arm])
```

---

## 7. 트러블슈팅

| 오류 | 원인 | 해결 |
|------|------|------|
| `ERROR 303` | 대학 네트워크 미연결 | 교내 Wi-Fi 또는 대학 VPN 연결 후 재시도 |
| `grbgetkey: command not found` | Gurobi 미설치 | `conda install -c gurobi gurobi` 먼저 실행 |
| `No Gurobi license found` | 라이선스 파일 경로 오류 | `GRB_LICENSE_FILE` 환경변수 확인 |
| `License expired` | 라이선스 만료 | User Portal에서 갱신 요청 |
| `Communication failed` | 네트워크 문제 | 방화벽/프록시 확인, VPN 재연결 |

---

## 📌 빠른 시작 체크리스트

```
[ ] gurobi.com 대학 이메일로 Academic 계정 가입
[ ] User Portal → Licenses → GENERATE NOW (Named-User Academic)
[ ] 라이선스 설치 아이콘 클릭 → grbgetkey 명령어 복사
[ ] 대학 네트워크(교내 Wi-Fi 또는 VPN) 연결
[ ] conda activate ogc2025
[ ] conda install -c gurobi gurobi
[ ] grbgetkey xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx 실행
[ ] (별도 경로 저장 시) GRB_LICENSE_FILE 환경변수 설정
[ ] python -c "import gurobipy as gp; gp.Model()" 로 확인
```
