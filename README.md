# Go2 Locomotion

Unitree Go2 사족보행 로봇의 강화학습 기반 보행 제어 연구 프로젝트.

Isaac Lab 3.0 External Project를 기반으로 구성하며,
로봇 모델과 설정은 독립적으로 관리하고
학습 환경 및 강화학습 알고리즘은 기존 프레임워크를 재사용한다.

## 1. 개발 환경과 문서

Ubuntu 22.04, RTX 3060 12GB, Python 3.12와 uv를 사용한다.
Isaac Sim 없이 Newton + MuJoCo Warp로 실행하며 시각화는 Newton GL을 사용한다.

- [환경 설치 및 USD 복원](docs/environment.md)
- [현재 구현과 설정 상속 구조](docs/architecture.md)
- [협업 및 변경 규칙](AGENTS.md)
- [공통 Isaac Lab 버전 기록](docs/isaaclab_version.txt)

## 2. 설치 및 환경 구성

공통 Isaac Lab과 Go2 프로젝트를 독립적으로 관리한다.

    ~/
    ├── IsaacLab/
    └── go2/
        └── go2_locomotion/
            ├── .venv/
            ├── pyproject.toml
            └── uv.lock

가상환경 설치:

    env -u PYTHONPATH uv sync --locked

Isaac Lab은 로컬 소스를 editable dependency로 참조한다.
프로젝트 경로가 변경되면 pyproject.toml의
[tool.uv.sources] 경로를 확인해야 한다.

새 PC에서는 [설치 순서](docs/environment.md)를 먼저 따른다.
이 저장소를 clone하는 것만으로 공통 Isaac Lab과 로봇 USD까지 설치되지는 않는다.

## 3. 프로젝트 구조

    go2_locomotion/
    ├── src/go2_locomotion/
    │   ├── assets/
    │   │   ├── go2_cfg.py
    │   │   ├── paths.py
    │   │   └── data/go2/
    │   ├── terrains/
    │   │   ├── flat.py
    │   │   ├── rough.py
    │   │   └── evaluation.py
    │   └── tasks/locomotion/
    │       ├── velocity_env_cfg.py
    │       ├── mdp/
    │       │   ├── __init__.py
    │       │   ├── rewards.py
    │       │   ├── observations.py
    │       │   ├── actions.py
    │       │   ├── commands.py
    │       │   ├── events.py
    │       │   ├── terminations.py
    │       │   └── curriculums.py
    │       └── config/go2/
    │           ├── __init__.py
    │           ├── flat_env_cfg.py
    │           ├── rough_env_cfg.py
    │           └── agents/
    │               └── rsl_rl_ppo_cfg.py
    ├── scripts/
    │   └── restore_assets.py
    ├── tests/
    ├── configs/
    ├── docs/
    ├── logs/
    ├── checkpoints/
    ├── results/
    ├── pyproject.toml
    └── uv.lock

## 4. 코드 관리 방식

| 구성 요소 | 관리 방식 |
|---|---|
| Go2 USD 모델 | 독립 관리 |
| Go2 로봇 Cfg | 공식 코드 기반 독립 작성 |
| 평지 환경 | 공식 Flat 환경 상속 |
| 험지 환경 | 공식 Rough 환경 상속 |
| PPO 설정 | 공식 RSL-RL 설정 상속 |
| 기존 MDP 함수 | 명시적 import |
| 사용자 정의 MDP | 예약 파일, 미구현 |
| 사용자 정의 지형 | 예약 파일, 미구현 |
| 물리 엔진 | Newton + MuJoCo Warp |
| 학습 및 재생 | Isaac Lab 공식 CLI |

공식 Isaac Lab 소스는 수정하지 않는 것을 원칙으로 한다.

현재 MDP 개별 모듈, 지형 모듈, velocity_env_cfg.py 및
일부 scripts 파일은 향후 연구를 위한 예약 파일이다.
`scripts/restore_assets.py`는 모델 복원 도구이고,
`scripts/list_envs.py`는 공식 CLI를 호출하는 호환 래퍼이다.

## 5. 로봇 기본 설정

| 항목 | 설정값 |
|---|---|
| 액추에이터 모델 | DCMotorCfg |
| 초기 몸체 높이 | 0.4 m |
| Kp | 25.0 |
| Kd | 0.5 |
| 액추에이터 마찰 | 0.0 |
| Soft joint position limit factor | 0.9 |
| Self collision | False |
| Contact sensor | True |

### 관절별 액추에이터 제한

| 관절 | 토크 제한 (Nm) | 속도 제한 (rad/s) |
|---|---:|---:|
| Hip | 23.7 | 30.1 |
| Thigh | 23.7 | 30.1 |
| Calf | 45.43 | 15.70 |

초기 설정은 공식 Isaac Lab Go2 모델과 동일하게 유지한다.

## 6. 등록된 Task

| Task ID | 설명 |
|---|---|
| Research-Go2-Flat | 평지 속도 추종 보행 |
| Research-Go2-Rough | 험지 속도 추종 보행 |

등록된 환경 확인:

    uv run isaaclab list_envs --show_presets

## 7. 실행 방법

### Zero Agent

    uv run isaaclab zero_agent \
        --task Research-Go2-Flat \
        --num_envs 4 \
        --viz newton_gl \
        physics=newton_mjwarp

### 평지 보행 학습

    uv run isaaclab train \
        --rl_library rsl_rl \
        --task Research-Go2-Flat \
        --num_envs 512 \
        --viz none \
        --seed 42 \
        --run_name learning \
        physics=newton_mjwarp

### 학습된 정책 재생

    uv run isaaclab play \
        --rl_library rsl_rl \
        --task Research-Go2-Flat \
        --checkpoint latest \
        --num_envs 4 \
        --viz newton_gl \
        physics=newton_mjwarp

### TensorBoard

    uv run tensorboard --logdir logs --port 6006

브라우저 접속: http://localhost:6006

### GPU 사용량 확인

    watch -n 0.5 nvidia-smi

### 에디터 설정

    uv run isaaclab --editor

### 테스트 및 코드 품질 검사

    env -u PYTHONPATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --locked pytest -q

이 검사는 Task 등록과 모델 경로·복원 처리를 확인하며 학습이나 시뮬레이션을 실행하지 않는다.
ROS의 Python 경로와 관계없는 pytest 플러그인이 개입하지 않도록 환경 변수를 지정한다.

Git 훅은 선택적으로 설치할 수 있다.

    uv run --locked pre-commit install
    uv run --locked pre-commit run --all-files

pre-commit에는 자동 포맷 및 수정 훅이 포함되어 있으므로 파일이 변경될 수 있다.

## 8. 실행 확인 상태

2026-11-25에 평지 학습과 CUDA 기반 정책 재생을 실행 확인하였다.
최초 실행은 설치 및 학습 경로 확인용이며 정책 성능의 비교 기준으로 사용하지 않는다.
험지 환경의 실제 학습 및 재생은 추가 검증이 필요하다.

## 9. Git 관리

소스 코드, 설정 파일, 문서 및 의존성 정보를 Git으로 관리한다.

다음 데이터는 Git 추적에서 제외한다.

- Python 가상환경
- 학습 로그
- 체크포인트
- 학습된 정책 파일
- 캐시 및 임시 파일
- 로봇 USD 모델 데이터

USD 모델은 재배포 라이선스 확인 전까지 로컬에서 관리한다.
새로운 PC에서 프로젝트를 실행하려면 모델 복원이 필요하다.

모델 원본:

https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/6.2/Isaac/IsaacLab/Robots/Unitree/Go2/go2.usd

모델 복원:

    env -u PYTHONPATH uv run --locked python scripts/restore_assets.py

현재 모델 검사만 수행:

    env -u PYTHONPATH uv run --locked python scripts/restore_assets.py --check

기존 모델이 있으면 다시 다운로드하지 않는다.
새로 다운로드한 모델은 참조 관계 검사 후 로컬 manifest에 경로와 SHA-256을 기록한다.
자동 네트워크 접근은 Task import나 학습 시작 시 수행하지 않는다.
다른 PC로 복원하는 방법과 해시 검사의 범위는 [환경 문서](docs/environment.md)에 설명한다.

GitHub에는 소스와 문서를 push하고, 학습 로그와 모델 데이터는 별도로 보관한다.
`baseline-v0.1.0`은 최초 실행 확인 시점의 기존 태그로 유지한다.
기능 수정은 별도 브랜치에서 진행하고, 변경 검토 후 `main`에 반영한다.

## 10. 연구 계획

- [x] Isaac Lab 및 Newton 환경 구축
- [x] 독립적인 Go2 External Project 구축
- [x] Go2 로봇 모델 및 설정 독립 관리
- [x] 평지 및 험지 Task 등록
- [x] 평지 학습 실행 확인
- [x] 학습된 정책 재생
- [x] GitHub 초기 버전 백업
- [x] 명시적 로봇 모델 복원 및 참조 검사 도구
- [ ] 보행 환경 및 제어 구조 분석
- [ ] 관측 공간 및 행동 공간 분석
- [ ] 보상함수 설계
- [ ] 관절 제한 및 Constraint RL
- [ ] 액추에이터 모델링
- [ ] 험지 보행
- [ ] Domain Randomization
- [ ] 외란 대응 및 보행 안정성
- [ ] 다리 손상 상황에서의 보행
- [ ] Sim2Sim
- [ ] Sim2Real
- [ ] Loco-Manipulation
