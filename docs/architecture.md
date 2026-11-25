# 현재 구현과 공부 순서

## 프로젝트의 역할

이 프로젝트는 Go2 기본 보행을 대상으로 강화학습과 Isaac Lab의 제어 흐름을 공부한다.
공통 프레임워크는 `/home/noh/IsaacLab`에 두고 프로젝트에서 editable 의존성으로 사용한다.
로봇 설정과 모델은 프로젝트 내부에서 관리하고 환경과 PPO는 공식 구현을 상속한다.

## Task가 등록되는 흐름

1. `pyproject.toml`의 `isaaclab.tasks` entry point가 `go2_locomotion.tasks`를 가리킨다.
2. 공식 CLI의 `load_external_tasks()`가 설치된 프로젝트의 entry point를 읽는다.
3. 자체 `tasks/__init__.py`가 `import_packages()`로 Task 패키지를 탐색한다.
4. `tasks/locomotion/config/go2/__init__.py`가 Gymnasium에 두 Task를 등록한다.
5. 각 등록은 자체 환경 Cfg와 자체 RSL-RL Cfg를 지정한다.

| Task | 환경 설정 | PPO 설정 |
|---|---|---|
| `Research-Go2-Flat` | `Go2FlatEnvCfg` | `Go2FlatPPORunnerCfg` |
| `Research-Go2-Rough` | `Go2RoughEnvCfg` | `Go2RoughPPORunnerCfg` |

환경 entry point는 둘 다 `isaaclab.envs:ManagerBasedRLEnv`이다.

## 환경 설정 상속

```text
공식 LocomotionVelocityRoughEnvCfg
└── 공식 UnitreeGo2RoughEnvCfg
    ├── 자체 Go2RoughEnvCfg
    └── 공식 UnitreeGo2FlatEnvCfg
        └── 자체 Go2FlatEnvCfg
```

자체 Flat과 Rough 클래스는 `super().__post_init__()` 뒤 `self.scene.robot`을
프로젝트의 `GO2_CFG`로 교체한다. 현재 관측·명령·보상·종료·이벤트는 부모 설정을 사용한다.
공통으로 예약한 자체 `velocity_env_cfg.py`는 이 상속 관계에 연결되어 있지 않다.

`GO2_CFG`는 공식 `UNITREE_GO2_CFG` 정의를 프로젝트로 가져온 독립 설정이다.
공식 객체를 import해 그대로 사용하는 방식이 아니므로 공식 로봇 설정의 후속 변경이
자동으로 반영되지는 않는다. 현재 수치와 원본 헤더를 유지하며 로컬 USD 경로를 사용한다.
모델 경로 선택은 `assets/paths.py`가 담당하고 복원 방식은 [환경 문서](environment.md)를 따른다.

## 현재 활성 설정

| 항목 | 설정과 근거 |
|---|---|
| 물리 엔진 | 공통 `RoughPhysicsCfg`의 기본값은 `newton_mjwarp`; 실행 명령에도 명시 |
| 물리 timestep | 공통 환경의 `sim.dt = 0.005 s` |
| Decimation | 공통 환경의 `4` |
| 정책 step | `step_dt = sim.dt × decimation = 0.02 s` |
| 물리 내부 substeps | Newton 설정의 `num_substeps = 2`; decimation과 구분 |
| 행동 | `JointPositionActionCfg`, Go2의 scale은 `0.25`, 기본 관절각 offset 사용 |
| Flat 지형 | plane, height scanner와 height scan 관측 제거 |
| 액추에이터 설정 | 자체 `DCMotorCfg`; 공식 Go2 환경에서 `use_newton_actuators = True` |
| PPO | 공식 설정 상속; 자체 클래스는 실험 이름을 `go2_flat`·`go2_rough`로 변경 |

Newton 내부 액추에이터 경로가 활성화되어 있으므로 Python의 `DCMotor.compute()`만 보고
현재 토크 계산 경로를 설명하지 않는다. Newton의 액추에이터 연결과 실행 구현도 확인한다.
관절 위치의 soft limit, 액추에이터 제한, 물리 엔진 제한은 이름만으로 동일시하지 않는다.

## 구현한 것과 예약한 것

| 파일 또는 디렉터리 | 현재 상태 |
|---|---|
| `assets/go2_cfg.py` | 독립 Go2 설정 |
| `assets/paths.py` | 기존 설치와 복원 manifest의 모델 경로 선택 |
| `tasks/locomotion/config/go2/` | Flat·Rough Task, 환경·PPO 상속 설정 |
| `tasks/locomotion/mdp/__init__.py` | 공식 함수와 Cfg의 명시적 재노출; 환경을 직접 변경하지 않음 |
| MDP의 개별 `.py` 파일 | docstring만 있는 예약 파일 |
| 자체 `velocity_env_cfg.py` | 예약 파일, 현재 상속 관계에 미연결 |
| `terrains/`의 지형 파일 | 예약 파일, 현재 공식 지형 사용 |
| `scripts/restore_assets.py` | 명시적 모델 복원과 읽기 전용 검사 |
| `scripts/list_envs.py` | 공식 CLI 호출 래퍼 |
| `scripts/train.py`, `play.py`, `evaluate.py`, `export_policy.py`, `sim2sim.py` | 예약 파일 |
| `tests/` | Task 등록과 모델 경로·복원 처리 검증 |

학습과 재생은 예약 스크립트가 아니라 공식 `isaaclab train`과 `isaaclab play`로 실행한다.
공식 재생에서 생성된 정책 export 파일이 있더라도 자체 `export_policy.py`가 구현되었다는 뜻은 아니다.
최초 평지 학습은 실행 확인 기록이며 정책 성능의 기준점으로 취급하지 않는다.
험지의 실제 학습·재생과 별도 PC 재설치는 아직 검증 대상으로 남아 있다.

## 공부 순서와 실제 소스 위치

아래 공식 경로는 Isaac Lab 저장소 기준이다.

1. Task 탐색: `source/isaaclab/isaaclab/cli/__init__.py`의 `load_external_tasks()`와 자체 등록 파일.
2. 최종 설정 구성: 공식 `source/isaaclab_tasks/isaaclab_tasks/core/velocity/config/go2/`와 자체 환경 Cfg.
3. 관측·명령·행동: 공식 `core/velocity/velocity_env_cfg.py`, `source/isaaclab/isaaclab/envs/mdp/`.
4. 제어 주기: `source/isaaclab/isaaclab/envs/manager_based_rl_env.py`의 `step()`.
5. 액추에이터: 자체 `GO2_CFG`, 공식 `actuators/actuator_pd.py`,
   `source/isaaclab_newton/isaaclab_newton/assets/articulation/actuator_control.py`.
6. 물리 연산: `source/isaaclab_newton/isaaclab_newton/physics/`와 실제 선택된 solver.
7. 보상·종료·리셋: 공통 환경 Cfg에서 연결된 함수와 각 Manager의 호출 순서.
8. PPO: `source/isaaclab_rl/isaaclab_rl/entrypoints/backends/train_rsl_rl.py`에서 RSL-RL runner로 이어지는 흐름.

각 단계를 설명할 때 호출 파일, 최종 설정값, 텐서 차원과 물리량 단위를 확인한다.
기능 변경은 이 연결을 확인한 뒤 하나의 주요 변수를 대상으로 진행한다.

## 공식 근거 자료

아래 링크는 현재 사용하는 Isaac Lab commit으로 고정한다.

- [공통 보행 환경](https://github.com/isaac-sim/IsaacLab/blob/e3f7d9ff1f5d7f8280de3ece9000b7117f66bcf4/source/isaaclab_tasks/isaaclab_tasks/core/velocity/velocity_env_cfg.py)
- [공식 Go2 설정](https://github.com/isaac-sim/IsaacLab/tree/e3f7d9ff1f5d7f8280de3ece9000b7117f66bcf4/source/isaaclab_tasks/isaaclab_tasks/core/velocity/config/go2)
- [ManagerBasedRLEnv](https://github.com/isaac-sim/IsaacLab/blob/e3f7d9ff1f5d7f8280de3ece9000b7117f66bcf4/source/isaaclab/isaaclab/envs/manager_based_rl_env.py)
- [Newton 액추에이터 연결](https://github.com/isaac-sim/IsaacLab/blob/e3f7d9ff1f5d7f8280de3ece9000b7117f66bcf4/source/isaaclab_newton/isaaclab_newton/assets/articulation/actuator_control.py)
