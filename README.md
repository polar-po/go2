# Go2 Locomotion

Unitree Go2 사족보행 로봇의 강화학습 기반 보행 제어 연구 프로젝트.

Isaac Lab 3.0 External Project를 기반으로 구성하며,
로봇 모델과 설정은 독립적으로 관리하고
학습 환경 및 강화학습 알고리즘은 기존 프레임워크를 재사용한다.

## 1. 개발 환경

| 항목 | 설정 |
|---|---|
| OS | Ubuntu 22.04 |
| GPU | NVIDIA RTX 3060 12GB |
| Python | 3.12.13 |
| 패키지 관리자 | uv |
| Isaac Lab | 3.0 |
| PyTorch | 2.11.0+cu130 |
| Newton | 1.6.1 |
| MuJoCo | 3.12.0 |
| MuJoCo Warp | 3.12.0 |
| NVIDIA Warp | 1.17.0 |
| RSL-RL | 5.5.1 |
| 물리 엔진 | newton_mjwarp |
| 시각화 | newton_gl |

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

    uv sync

Isaac Lab은 로컬 소스를 editable dependency로 참조한다.
프로젝트 경로가 변경되면 pyproject.toml의
[tool.uv.sources] 경로를 확인해야 한다.

## 3. 프로젝트 구조

    go2_locomotion/
    ├── src/go2_locomotion/
    │   ├── assets/
    │   │   ├── go2_cfg.py
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
| 사용자 정의 MDP | 직접 구현 |
| 사용자 정의 지형 | 직접 구현 |
| 물리 엔진 | Newton + MuJoCo Warp |
| 학습 및 재생 | Isaac Lab 공식 CLI |

공식 Isaac Lab 소스는 수정하지 않는 것을 원칙으로 한다.

현재 MDP 개별 모듈, 지형 모듈, velocity_env_cfg.py 및
일부 scripts 파일은 향후 연구를 위한 예약 파일이다.

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
        --run_name baseline \
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

    uv run pytest
    uv run pre-commit run --all-files

전체 테스트 및 코드 품질 검사 통과 여부는 별도 검증이 필요하다.

## 8. Baseline 학습 결과

최초 학습일: 2026-11-25

기준 태그: baseline-v0.1.0

| 항목 | 결과 |
|---|---:|
| 병렬 환경 | 512 |
| Learning iterations | 300 |
| Total steps | 3,686,400 |
| 최종 Steps per second | 48,394 |
| Training time | 78.68 s |
| Mean reward | 2.63 |
| Mean episode length | 901.22 |
| XY velocity error | 0.8802 |
| Yaw velocity error | 0.3145 |
| Time-out termination | 0.8182 |
| Base-contact termination | 0.1818 |
| Success rate | 0.0000 |

위 결과는 마지막 학습 iteration 기준이며,
독립적인 정책 성능 평가 결과는 아니다.

평지 학습 및 CUDA 기반 정책 재생을 확인하였다.
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

모델 다운로드에는 Isaac Lab의 retrieve_file_path()를 사용한다.

다운로드 이후 실제 USD 경로가 go2_cfg.py의
GO2_USD_PATH와 일치하는지 확인해야 한다.

모델 자동 복원 기능은 추후 구현한다.

## 10. 연구 계획

- [x] Isaac Lab 및 Newton 환경 구축
- [x] 독립적인 Go2 External Project 구축
- [x] Go2 로봇 모델 및 설정 독립 관리
- [x] 평지 및 험지 Task 등록
- [x] 평지 Baseline 학습
- [x] 학습된 정책 재생
- [x] GitHub 초기 버전 백업
- [ ] 로봇 모델 자동 복원
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

