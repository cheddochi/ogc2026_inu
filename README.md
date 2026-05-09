# OGC 2025 - 개발환경 및 베이스라인 알고리즘 가이드

## 📋 목차
- [Update History](#update-history)
- [1. 환경설정](#1-환경설정)
- [2. 알고리즘 제출 방법](#2-알고리즘-제출-방법)
- [3. alg_tester 사용법](#3-alg_tester-사용법)

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

### 추가 설치 패키지 (요청 반영)

| 패키지 | 버전 |
|--------|------|
| torch_cluster | 1.6.3+pt26cu124 |
| torch-geometric | 2.6.1 |
| torch_scatter | 2.1.2+pt26cu124 |
| torch_sparse | 0.6.18+pt26cu124 |
| torch_spline_conv | 1.2.2+pt26cu124 |
| cdlib | 0.4.0 |
| leidenalg | 0.10.2 |
| stable_baselines3 | 2.6.0 |

> 위 패키지들은 conda 환경 파일에 포함되어 있지 않으므로 필요 시 별도 설치하세요.

---

### Conda 환경 설정

Conda 설치에는 **miniforge** 사용을 권장합니다.

#### 설치 절차

**1단계.** 환경 설정 파일 다운로드
```
ogc2025_env_20250506.yml.zip
```
임의의 폴더에 저장 후 압축 해제합니다.

**2단계.** 해당 폴더로 이동 후 환경 생성
```bash
conda env create -f ogc2025_env_2025XXXX.yml
```
> ⚠️ `ogc2025_env_2025XXXX.yml`은 실제 다운로드한 파일명으로 변경하세요.

**3단계.** 환경 활성화
```bash
conda activate ogc2025
```
터미널에 `(ogc2025)`가 표시되면 환경 설정 완료입니다.

> 💡 **설치 오류 발생 시**: pytorch, tensorflow 등 사용하지 않는 패키지는 yml 파일에서 해당 항목을 삭제 후 재설치하세요. 문제가 지속되면 Slack 채널로 문의하세요.

---

## 2. 알고리즘 제출 방법

### 필요 파일 다운로드

```
baseline_20250719.zip          ← 알고리즘 예제 코드
exercise_problems_20250512.zip ← 연습 문제
```

> 💡 두 파일 모두 버그 수정 등으로 업데이트될 수 있으니 주기적으로 최신 버전을 확인하세요.  
> 💡 `exercise_problems`는 예선 평가 문제가 아닌 연습 문제입니다. 평가 문제는 각 단계 종료 후 공개됩니다.

---

### 베이스라인 파일 구조

```
baseline/
├── myalgorithm.py   ← 알고리즘 구현 파일 (가장 중요!)
└── util.py          ← 알고리즘 구현 보조 함수 모음
```

---

### myalgorithm.py 작성 방법

`algorithm()` 함수 안의 지정된 구간에 알고리즘을 작성합니다.

```python
def algorithm(prob_info, timelimit=60):
    """
    파라미터:
        prob_info  : 문제 데이터
        timelimit  : 실행 제한 시간(초) - 이 시간 내에 반드시 종료해야 함
    """

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
    # 항구번호: [(경로, 수요번호), ...]
    0: [
        [[0, 1, 3, 5, 6, 9, 15, 20, 22], 2],
        [[0, 1, 2, 4, 7, 10, 14, 19, 21], 2],
        ...
    ],
    1: [
        [[9, 6, 5, 3, 1, 0], 0],
        ...
    ]
}
```

- **항구번호**: `0 ~ P-1`
- **경로**: `[0, 3, 2]` 와 같이 노드 목록
- **수요번호**: `K` 리스트의 인덱스 (`0 ~ len(K)-1`)

---

### 해 유효성 검증

`util.py`의 `check_feasibility()` 함수로 반드시 검증하세요.

```python
result = check_feasibility(prob_info, solution)
# {
#     'obj': 588.0,       # 목적 함수 (총 경로 비용 - LB)
#     'feasible': True,   # 해 유효 여부
#     'infeasibility': None  # 유효하지 않을 경우 사유
# }
```

> ⚠️ 실행 시간은 `algorithm()` 함수 순수 실행 시간(wall clock 기준)으로 측정됩니다. 제한 시간 초과 시 결과와 무관하게 penalty 점수가 부여됩니다.

---

### 제출 규칙

압축 파일 제출 시 다음 조건을 만족해야 합니다.

- **형식**: `.zip` 파일 (파일명 자유)
- **필수 파일**: `myalgorithm.py`, `util.py`
- `myalgorithm.py`는 **압축 파일 최상위**에 위치해야 함 (하위 폴더 불가)
- `util.py` 수정 불가 (수정 제출 시 원본으로 replace 후 평가)
- 추가 Python 파일 및 모델 파일은 별도 폴더에 포함 가능
- **최대 파일 크기**: 30MB (초과 시 Slack 채널에서 증가 요청)

**MacOS/Linux에서 압축 파일 구조 확인:**
```bash
unzip -vl 압축파일.zip
```
> `myalgorithm.py`가 하위 폴더 아래에 있으면 안 됩니다.

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

다른 언어 사용도 가능하나, 다음 사항을 반드시 준수해야 합니다.

- 필요한 라이브러리를 **모두 압축 파일에 포함**하여 제출
- `myalgorithm.py`에서 해당 언어의 함수를 호출하도록 작성
- 평가 서버에서 **컴파일을 수행하지 않으므로** 사전에 빌드 후 바이너리 포함
- 평가 서버 환경: **Linux/Ubuntu 24.04**

**Java 설치 예시:**
```bash
sudo apt-get update
sudo apt-get install openjdk-17-jdk
java --version
```

**C# (Dotnet) 설치 예시:**
```bash
sudo apt install -y dotnet-runtime-8.0
dotnet --info
```

> 💡 Julia 등 별도 컴파일이 필요 없는 언어도 Slack 채널을 통해 사용 가능 여부를 먼저 확인하세요.

---

## 3. alg_tester 사용법

제출 전 알고리즘 동작 및 압축 형식을 로컬에서 검증할 수 있습니다.

### 사용 방법

**1단계.** 파일 다운로드 및 압축 해제
```
alg_tester_20250513.zip
```

**2단계.** 노트북 실행
```bash
# ogc2025 환경 활성화 후
conda activate ogc2025
jupyter lab
```
`alg_tester.ipynb` 파일을 열고 첫 번째 셀을 실행(`Ctrl + Enter`)합니다.

### 주요 기능

- 제출 압축 파일의 형식 및 `algorithm()` 함수 존재 여부 검증
- 여러 문제 파일에 대해 알고리즘 실행 및 결과 확인
- 유효한 해의 목적 함수 계산 및 시각화
- 여러 알고리즘 × 여러 문제 조합 일괄 실행 및 결과 비교

> ⚠️ `alg_tester`에서 정상 동작해도 평가 서버 환경 차이로 오류가 발생할 수 있습니다. 가능하면 Ubuntu 24.04 가상 환경에서도 사전 검증을 권장합니다.

---

## 📌 빠른 시작 체크리스트

```
[ ] miniforge 설치
[ ] conda env create -f ogc2025_env_2025XXXX.yml 실행
[ ] conda activate ogc2025
[ ] baseline_20250719.zip 및 exercise_problems_20250512.zip 다운로드
[ ] myalgorithm.py에 알고리즘 작성
[ ] check_feasibility()로 해 유효성 검증
[ ] alg_tester로 제출 형식 검증
[ ] zip 파일 압축 (myalgorithm.py가 최상위에 위치하는지 확인)
[ ] 제출
```
