# OGC 2024 - 개발환경 및 베이스라인 알고리즘 가이드

## 📋 목차
- [Update History](#update-history)
- [1. 환경설정](#1-환경설정)
- [2. 알고리즘 제출 방법](#2-알고리즘-제출-방법)
- [3. Baseline 알고리즘 실행 방법](#3-baseline-알고리즘-실행-방법)
- [4. 상용 최적화 Solver 라이센스 발급](#4-상용-최적화-solver-라이센스-발급)

---

## Update History

| 날짜 | 내용 |
|------|------|
| 2024/09/10 | `ogc2024_env.yml` 업데이트 — `scikit-learn-extra` 패키지 사용 가능 |
| 2024/07/20 | `baseline_20240720.zip` 업데이트 |
| 2024/07/12 | Java (openjdk 17.0.11) 사용 가능 |
| 2024/07/01 | `baseline_20240701.zip` 업데이트 |
| 2024/06/29 | 알고리즘 제출 시 압축파일 형태 확인 설명 추가 |
| 2024/06/24 | 알고리즘 실행 결과 error code 설명 추가 |
| 2024/06/21 | `baseline_20240621.zip` 업데이트 |
| 2024/06/16 | `baseline_20240616.zip` 업데이트 |
| 2024/06/03 | `Microsoft.NETCore.App 7.0.19` 사용 가능 |
| 2024/05/17 | 상용 최적화 솔버 라이센스 발급 관련 내용 추가 |
| 2024/05/17 | `baseline_20240517.zip` 업데이트 |

---

## 1. 환경설정

알고리즘 제출 전, 개인 PC에서 평가 서버와 동일한 Python 환경을 구성해야 합니다.

### 사용 가능한 Python 패키지

| 패키지 | 버전 |
|--------|------|
| python | 3.10 |
| jupyterlab | 4.0.11 |
| matplotlib | 3.8.4 |
| pandas | 2.2.1 |
| networkx | 3.1 |
| scipy | 1.12.0 |
| tensorflow | 2.10.0 |
| keras | 2.10.0 |
| pytorch | 2.2.0 |
| scikit-learn | 1.3.0 |
| scikit-learn-extra | 0.3.0 |
| numba | 0.59.1 |
| cython | 3.0.10 |
| ortools | 9.9.3963 |
| gurobipy | 11.0.1 |
| xpress | 9.3 |

> 💡 필요한 패키지가 목록에 없으면 Slack 채널에서 요청하세요.

---

### Conda 환경 설정

#### 설치 절차

**1단계.** 환경 설정 파일 다운로드
```
ogc2024_env.yml
```
임의의 폴더에 저장합니다.

**2단계.** 해당 폴더로 이동 후 환경 생성
```bash
conda env create -f ogc2024_env.yml
```

**3단계.** 환경 활성화
```bash
conda activate ogc2024
```
터미널에 `(ogc2024)`가 표시되면 환경 설정 완료입니다.

---

## 2. 알고리즘 제출 방법

### 필요 파일 다운로드

```
baseline_20240720.zip              ← 알고리즘 예제 코드
alg_test_problems_20240429.zip     ← baseline 실행용 예제 문제
```

> 💡 두 파일 모두 버그 수정 등으로 업데이트될 수 있으니 주기적으로 최신 버전을 확인하세요.  
> 💡 `alg_test_problems`는 예선 평가 문제가 아닙니다. 각 단계의 문제는 해당 단계 시작 시 공개됩니다.

---

### 베이스라인 파일 구조

```
baseline/
├── myalgorithm.py    ← 알고리즘 구현 파일 (가장 중요!)
├── util.py           ← 알고리즘 구현 보조 함수 모음
└── alg_test.ipynb    ← 알고리즘 테스트용 Jupyter Notebook
```

---

### myalgorithm.py 작성 방법

`algorithm()` 함수 안의 지정된 구간에 알고리즘을 작성합니다.

```python
from util import *

def algorithm(K, all_orders, all_riders, dist_mat, timelimit=60):
    """
    파라미터:
        K          : 주문 개수
        all_orders : 주문 list
        all_riders : 배달원 list
        dist_mat   : 거리 행렬 (distance matrix)
        timelimit  : 실행 제한 시간(초) - 이 시간 내에 반드시 종료해야 함
    """

    start_time = time.time()

    for r in all_riders:
        r.T = np.round(dist_mat / r.speed + r.service_time)

    solution = []

    #------------- Custom algorithm code starts from here --------------#

    # 여기에 알고리즘 코드를 작성하세요

    #------------- End of custom algorithm code --------------#

    return solution
```

> ⚠️ `myalgorithm.py` 파일명과 `def algorithm(K, all_orders, all_riders, dist_mat, timelimit=60):` 함수 시그니처는 **절대 변경 불가**합니다.

---

### 해(solution) 형식

```python
# [배달원 종류, 음식점 방문 순서, 고객 방문 순서] 의 리스트를 반환
solution = [
    ["BIKE", [1, 3, 2], [2, 3, 1]],
    # 의미: 주문 1·2·3을 오토바이 배달원에 할당,
    #       픽업은 1→3→2 순서, 배달은 2→3→1 순서로 방문
    ...
]
```

---

### 제출 규칙

압축 파일 제출 시 다음 조건을 반드시 만족해야 합니다.

- **형식**: `.zip` 파일 (파일명 자유)
- **필수 파일**: `myalgorithm.py`, `util.py`
- `myalgorithm.py`는 **압축 파일 최상위**에 위치해야 함 (하위 폴더 불가)
- `alg_test.ipynb`는 제출하지 않아도 무관
- `util.py` 수정 불가 (수정 제출 시 원본으로 replace 후 평가)
- 추가 Python 파일 및 모델 파일은 별도 폴더에 포함 가능
- **최대 파일 크기**: 30MB (초과 시 Slack 채널에서 증가 요청)

**MacOS/Linux에서 압축 파일 구조 확인:**
```bash
unzip -vl 압축파일.zip
```
> `myalgorithm.py`가 하위 폴더 아래에 있으면 제출 불가입니다.

---

### 에러 코드 안내

| 에러 코드 | 설명 |
|-----------|------|
| `alg_error` | 알고리즘 실행 중 Python exception 발생 |
| `infeasible` | 도출한 해가 유효하지 않음 |
| `time_limit` | 실행 시간이 제한을 초과함 |
| `sys_error(03)` | 압축 파일 해제 실패 (잘못된 형식) |
| `sys_error(05)` | 최상위 폴더에 `myalgorithm.py` 없음 |
| `test_error(01)` | `ogc2024` 환경에 없는 패키지 import 시도 |

> 세부 에러코드는 대회 진행에 따라 추가될 수 있습니다.

---

### Python 외 언어 사용

다른 언어 사용도 가능하나, 다음 사항을 반드시 준수해야 합니다.

- 필요한 라이브러리를 **모두 압축 파일에 포함**하여 제출
- `myalgorithm.py`에서 해당 언어의 함수를 호출하도록 작성
- 평가 서버에서 **컴파일을 수행하지 않으므로** 사전에 빌드 후 바이너리 포함
- 평가 서버 환경: **Linux/Ubuntu 22.04**
- Gurobi, Xpress, ORTools 등 MIP solver는 **Python 환경에서만** 사용 가능

> 💡 Julia 등 별도 컴파일이 필요 없는 언어도 Slack 채널을 통해 사용 가능 여부를 먼저 확인하세요.

**Java 설치 예시:**
```bash
sudo apt-get update
sudo apt-get install openjdk-17-jdk
java --version
```

**C# (Dotnet) 설치 예시:**
```bash
sudo apt install -y dotnet-runtime-7.0
dotnet --info
```

---

## 3. Baseline 알고리즘 실행 방법

`alg_test.ipynb` 노트북을 사용해 알고리즘 동작을 확인합니다.

> 💡 JupyterLab 또는 VSCode가 필요합니다. 노트북 실행 전 Jupyter kernel이 `ogc2024` 환경인지 반드시 확인하세요.

### 실행 방법

**1단계.** `ogc2024` 환경 활성화 후 JupyterLab 실행
```bash
conda activate ogc2024
jupyter-lab
```

**2단계.** `alg_test.ipynb` 열고 셀 순서대로 실행

---

### 주요 코드 설명

**문제 파일 설정**
```python
problem_file = '../alg_test_problems_20240429/TEST_K100_1.json'
timelimit = 10
```
각 단계별 문제가 공개되면 해당 파일 경로로 변경하세요.

**알고리즘 실행**
```python
solution = algorithm(K, ALL_ORDERS, ALL_RIDERS, DIST, timelimit)
```

**해 유효성 검증**
```python
checked_solution = solution_check(K, ALL_ORDERS, ALL_RIDERS, DIST, solution)
```

**결과 예시**
```python
{
    'total_cost': 573047.2,
    'avg_cost': 5730.472,        # 목적 함수 (평균 배달 비용)
    'num_drivers': 50,
    'feasible': True,            # 해 유효 여부
    'infeasibility': None,       # 유효하지 않을 경우 사유
    'time': 9.46,                # 알고리즘 실제 실행 시간 (wall clock)
    'timelimit_exception': False, # 시간 초과 여부
    'exception': None            # 예외 발생 여부
}
```

> ⚠️ `timelimit_exception`이 `True`가 되면 결과와 무관하게 penalty 점수가 부여됩니다.

**경로 시각화**
```python
draw_route_solution(ALL_ORDERS, checked_solution)         # 배달 경로 시각화
draw_bundle_solution(ALL_ORDERS, ALL_RIDERS, DIST, checked_solution)  # 묶음 배송 상세
```

> 💡 노트북 코드를 수정해도 실제 알고리즘은 `myalgorithm.py`에 있으므로 평가 서버 실행에 영향을 미치지 않습니다. 이 노트북은 **로컬 개발 및 디버깅** 전용입니다.

---

## 4. 상용 최적화 Solver 라이센스 발급

기본 제공 솔버인 Google ORTools 외에 상용 솔버 라이센스가 필요한 경우 아래로 문의하세요.

| 솔버 | 담당자 | 이메일 |
|------|--------|--------|
| Gurobi | 이강주 영업대표 | kangju.lee@gurobi.com |
| Xpress | 윤기섭 수석 | ricelove@optimasolution.co.kr |

### 라이센스 신청 시 유의사항

- **메일 제목**: `[OGC2024] 솔버 라이센스 신청 - 참가팀명`
- 솔버사 담당자가 경연 참가 여부 확인 후 라이센스 발급 진행
- **라이센스 유효기간**: 발급 시점 ~ 2024년 10월 말 (최대)
- 솔버 설치 및 사용 중 기술적 문제는 솔버사 담당자와 직접 협의

---

## 📌 빠른 시작 체크리스트

```
[ ] conda env create -f ogc2024_env.yml 실행
[ ] conda activate ogc2024
[ ] baseline_20240720.zip 및 alg_test_problems_20240429.zip 다운로드
[ ] alg_test.ipynb에서 baseline 알고리즘 정상 실행 확인
[ ] myalgorithm.py에 알고리즘 작성
[ ] solution_check()로 해 유효성 검증
[ ] zip 파일 압축 (myalgorithm.py가 최상위에 위치하는지 확인)
[ ] 제출
```
