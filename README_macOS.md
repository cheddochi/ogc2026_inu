# OGC 2025 - 개발환경 가이드 (macOS Apple Silicon)

> 🍎 **이 문서는 Apple Silicon (M1/M2/M3) + bash/zsh 환경 기준입니다.**  
> Windows PowerShell 환경은 `README_Windows.md`를 참고하세요.

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

### 추가 설치 패키지 (요청 반영)

| 패키지 | 서버 버전 | macOS 설치 비고 |
|--------|-----------|-----------------|
| torch_cluster | 1.6.3+pt26cu124 | CPU 전용 휠로 설치 |
| torch-geometric | 2.6.1 | 동일 |
| torch_scatter | 2.1.2+pt26cu124 | CPU 전용 휠로 설치 |
| torch_sparse | 0.6.18+pt26cu124 | CPU 전용 휠로 설치 |
| torch_spline_conv | 1.2.2+pt26cu124 | CPU 전용 휠로 설치 |
| cdlib | 0.4.0 | 동일 |
| leidenalg | 0.10.2 | 동일 |
| stable_baselines3 | 2.6.0 | 동일 |

> ⚠️ Apple Silicon은 CUDA를 지원하지 않습니다. 로컬에서는 CPU/MPS 모드로 동작하며, CUDA 전용 기능이 있다면 평가 서버(Linux+GPU)에서만 작동합니다.

---

### Conda 환경 설정

Apple Silicon에는 **Miniforge** (ARM64 네이티브) 사용을 권장합니다.

#### 1단계. Miniforge 설치

```bash
# Homebrew로 설치 (권장)
brew install miniforge

# 또는 직접 다운로드
curl -L https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh -o miniforge.sh
bash miniforge.sh
```

#### 2단계. 환경 생성

`ogc2025_env_20250506.yml.zip`을 다운로드하고 압축 해제 후 실행합니다.

```bash
# yml 파일이 있는 폴더로 이동
cd ~/Downloads

# 환경 생성
conda env create -f ogc2025_env_20250506.yml
```

> ⚠️ torch, tensorflow 설치 오류 시: Apple Silicon은 CUDA 빌드가 없어 yml 설치가 실패할 수 있습니다.  
> 해당 패키지를 yml에서 제거 후 아래와 같이 별도 설치하세요.

```bash
# torch Apple Silicon 전용 설치 (MPS 가속 지원)
pip install torch==2.6.0 torchvision==0.21.0
```

#### 3단계. 환경 활성화

```bash
conda activate ogc2025
```

터미널 프롬프트에 `(ogc2025)`가 표시되면 완료입니다.

---

## 2. 알고리즘 제출 방법

### 필요 파일 다운로드

```
baseline_20250719.zip          ← 알고리즘 예제 코드
exercise_problems_20250512.zip ← 연습 문제
```

> 💡 두 파일 모두 버그 수정 등으로 업데이트될 수 있으니 주기적으로 최신 버전을 확인하세요.  
> 💡 `exercise_problems`는 연습 문제입니다. 평가 문제는 각 단계 종료 후 공개됩니다.

```bash
# 압축 해제
unzip baseline_20250719.zip
unzip exercise_problems_20250512.zip

# 파일 목록 확인 (prob1.json ~ prob10.json 형식)
ls exercise_problems/
```

---

### 베이스라인 파일 구조

```
baseline/
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

```bash
# 압축 파일 구조 확인
unzip -vl submission.zip
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
- 평가 서버 환경: **Linux/Ubuntu 24.04** (ARM이 아닌 x86_64)

> ⚠️ macOS에서 빌드한 바이너리는 평가 서버(Linux x86_64)에서 실행되지 않습니다.  
> C/C++, Java 등을 사용하는 경우 반드시 Linux x86_64 환경에서 크로스 컴파일하거나 Docker를 활용하세요.

---

## 3. alg_tester 사용법

```bash
# ogc2025 환경 활성화 후
conda activate ogc2025
jupyter lab
```

`alg_tester.ipynb` 파일을 열고 첫 번째 셀을 실행(`Ctrl + Enter`)합니다.

> ⚠️ `alg_tester`에서 정상 동작해도 평가 서버 환경 차이로 오류가 발생할 수 있습니다.  
> macOS에서 통과해도 Ubuntu 24.04 기준이므로 가능하면 Docker나 VM으로 최종 검증을 권장합니다.

---

## 4. 로컬 테스트 환경 (커스텀)

공식 `alg_tester` 외에 터미널에서 바로 실행·검증·제출 패키지 빌드까지 가능한 커스텀 스크립트 셋입니다.

### 4-1. 프로젝트 파일 구조

```
ogc2025/
├── myalgorithm.py              ← 알고리즘 구현 (수정 대상)
├── util.py                     ← 유틸 함수 (수정 불가)
├── problem_generator.py        ← 테스트용 샘플 문제 생성기
├── requirements.txt            ← pip 의존 패키지 목록
├── run_test.sh                 ← 단일 문제 테스트 실행
├── run_all_tests.sh            ← 전체 사이즈 일괄 테스트
├── build_submit.sh             ← 제출용 zip 빌드 및 검증
├── install_extra_packages.sh   ← 추가 PyG 계열 패키지 설치
└── exercise_problems/          ← 공식 연습 문제 폴더
```

---

### 4-2. 환경 설치

```bash
# conda 환경 생성 및 활성화
conda env create -f ogc2025_env_20250506.yml
conda activate ogc2025

# 핵심 패키지 설치
pip install -r requirements.txt

# 추가 패키지 설치 (PyG 계열 등, 필요 시)
# macOS는 자동으로 CPU 전용 휠로 설치됩니다
bash install_extra_packages.sh
```

---

### 4-3. 테스트 실행

#### 공식 연습 문제로 직접 실행

```bash
# 연습 문제 압축 해제
unzip exercise_problems_20250512.zip

# 파일명은 prob1.json ~ prob10.json (prob_01 아님에 주의)
python myalgorithm.py prob1 exercise_problems/prob1.json 60
```

#### 스크립트로 단일 테스트

```bash
bash run_test.sh              # small 문제, 60초 제한 (기본값)
bash run_test.sh medium 120   # medium 문제, 120초 제한
```

> 문제 파일이 없으면 `problem_generator.py`로 샘플 문제를 자동 생성합니다.

#### 전체 사이즈 일괄 테스트

```bash
bash run_all_tests.sh         # 60초 제한
bash run_all_tests.sh 120     # 120초 제한
```

실행 결과 예시:
```
  [tiny]   ✅ feasible=True  obj=2.0   time=0.00s
  [small]  ✅ feasible=True  obj=24.0  time=0.00s
  [medium] ✅ feasible=True  obj=68.0  time=0.01s
  [large]  ✅ feasible=True  obj=142.0 time=0.03s
```

---

### 4-4. 샘플 문제 생성기

```bash
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

### 4-5. 제출 패키지 빌드

```bash
bash build_submit.sh                     # 타임스탬프 파일명 자동 생성
bash build_submit.sh my_submission.zip   # 파일명 직접 지정
```

스크립트가 자동으로 검증합니다:
- `myalgorithm.py`가 zip 최상위에 위치하는지
- 파일 크기 30MB 이하인지

---

### 4-6. 결과 확인

알고리즘 실행 후 `results.json`으로 결과가 저장됩니다.

```bash
cat results.json
```

```json
{
  "feasible": true,
  "obj": 24.0,
  "infeasibility": null,
  "time": 0.0029,
  "timelimit_exception": false,
  "prob_name": "prob1",
  "prob_file": "exercise_problems/prob1.json"
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

## 📌 빠른 시작 체크리스트 (macOS)

```
[ ] Miniforge 설치 (brew install miniforge)
[ ] conda env create -f ogc2025_env_20250506.yml
[ ] conda activate ogc2025
[ ] pip install -r requirements.txt
[ ] baseline_20250719.zip 및 exercise_problems_20250512.zip 다운로드
[ ] unzip exercise_problems_20250512.zip  → 파일명: prob1.json ~ prob10.json
[ ] myalgorithm.py에 알고리즘 작성
[ ] bash run_test.sh 로 단일 테스트
[ ] bash run_all_tests.sh 로 전체 사이즈 검증
[ ] check_feasibility()로 해 유효성 최종 확인
[ ] bash build_submit.sh 로 제출 패키지 빌드
[ ] alg_tester로 제출 형식 최종 검증
[ ] 제출
```
