# 환경 설치 및 모델 복원

## 기록된 환경

공통 프레임워크는 Isaac Lab 3.0 소스 checkout이며, 기준 commit은
`e3f7d9ff1f5d7f8280de3ece9000b7117f66bcf4`이다.
저장소 주소와 버전은 [isaaclab_version.txt](isaaclab_version.txt)에 기록한다.

| 항목 | 현재 환경의 기록 |
|---|---|
| OS / GPU | Ubuntu 22.04 / RTX 3060 12GB |
| Python | 3.12 계열; 프로젝트 지원 범위는 `>=3.12,<3.13` |
| 패키지 관리자 | uv |
| PyTorch / Torchvision | 2.11.0+cu130 / 0.26.0+cu130 |
| Newton | 1.6.1 |
| MuJoCo / MuJoCo Warp | 3.12.0 / 3.12.0 |
| NVIDIA Warp | 1.17.0 |
| RSL-RL | 5.5.1 |
| Gymnasium / TensorBoard | 1.4.0 / 2.21.0 |
| 물리 엔진 / 시각화 | `newton_mjwarp` / `newton_gl` |

패키지 버전은 현재 `uv.lock`과 설치된 패키지 메타데이터를 확인한 기록이다.
운영체제와 GPU는 프로젝트의 기존 환경 기록이다.
시스템 CUDA Toolkit과 PyTorch 패키지의 CUDA Runtime 버전을 동일시하지 않는다.
새 PC의 드라이버와 GPU 호환성은 별도로 확인한다.

## 새 PC에서의 설치 순서

아래는 uv와 Git을 설치한 Ubuntu에서, 대상 디렉터리가 아직 없을 때 사용하는 명령이다.
현재 PC의 기존 프로젝트를 다시 clone하거나 기존 Isaac Lab checkout을 변경하는 용도가 아니다.

```bash
mkdir -p ~/go2
git clone https://github.com/isaac-sim/IsaacLab.git ~/IsaacLab
git -C ~/IsaacLab checkout --detach e3f7d9ff1f5d7f8280de3ece9000b7117f66bcf4
git clone https://github.com/polar-po/go2.git ~/go2/go2_locomotion
cd ~/go2/go2_locomotion
env -u PYTHONPATH uv sync --locked
env -u PYTHONPATH uv run --locked python scripts/restore_assets.py
env -u PYTHONPATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --locked pytest -q
```

위 명령은 의존성과 모델을 네트워크에서 가져온다.
아직 `main`에 병합되지 않은 수정은 해당 작업 브랜치를 checkout한 뒤 사용한다.

`pyproject.toml`의 `../../IsaacLab`은 Go2 프로젝트에서의 상대 경로이다.
사용자 이름이 달라도 다음 배치를 유지하면 경로 변경이 필요 없다.

```text
~/
├── IsaacLab/
└── go2/
    └── go2_locomotion/
```

`uv.lock`은 로컬 Isaac Lab 소스의 Git commit을 고정하지 않는다.
기록된 commit과 로컬 변경 여부를 함께 확인한다.

```bash
git -C ~/IsaacLab rev-parse HEAD
git -C ~/IsaacLab status --short
```

공유 Isaac Lab을 다른 연구에서 사용 중이면 해당 checkout을 임의로 전환하지 않는다.
배치를 변경할 때는 `pyproject.toml`의 `[tool.uv.sources]`를 명시적으로 갱신하고,
의존성 변경으로서 `uv.lock`의 차이를 확인한다.

## USD 복원 방식

모델 원본은 Isaac Lab의 [Go2 USD](https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/6.2/Isaac/IsaacLab/Robots/Unitree/Go2/go2.usd)이다.
`scripts/restore_assets.py`는 모델이 없을 때만 공식 `retrieve_file_path()`로 의존 파일을 가져온다.

다운로드 위치는 `src/go2_locomotion/assets/data/go2/`이다.
생성되는 UUID 디렉터리 이름을 고정하지 않고, 반환된 USD의 상대 경로를
같은 디렉터리의 `asset_manifest.json`에 저장한다.
manifest와 USD는 해당 디렉터리 전체에 대한 `.gitignore` 규칙으로 Git 추적에서 제외된다.

- manifest가 있으면 기록된 `usd_path`를 사용한다.
- manifest가 없으면 기존 로컬 설치의 모델 경로를 사용한다.
- 기존 모델이 있으면 복원 명령은 검사만 수행하고 덮어쓰거나 재다운로드하지 않는다.
- Task import는 파일을 선택할 뿐 모델을 다운로드하지 않는다.

검사에서는 `UsdUtils.ComputeAllDependencies()`의 미해결 참조, USD Stage의 구성 오류,
default prim 유무, 의존 파일이 프로젝트 모델 디렉터리 안에 있는지를 확인한다.
현재 Go2의 `OmniPBR.mdl`은 렌더러가 해석하는 모듈 이름이므로 예외로 보고하며,
MDL 재질 렌더링까지 검증하지 않는다. 다른 미해결 파일은 오류로 처리한다.
새로 복원할 때 의존 파일의 SHA-256을 manifest에 기록한다.
이후 `--check`는 manifest가 있으면 복원 당시의 해시와 비교한다.
기존 모델에는 manifest가 없으므로 참조 검사만 수행하며 과거 내용과의 동일성을 보장하지 않는다.

연구 목적으로 모델을 수정하면 해시 불일치가 보고된다.
이는 편집 금지가 아니라 복원 당시 파일과의 차이를 알리는 검사이다.
검사 실패 시에도 모델은 덮어쓰지 않는다. 편집 내용과 기록의 처리 방법을 확인한 뒤 진행한다.

로컬화된 USD 참조는 절대 경로를 포함할 수 있다.
다른 PC로 UUID 폴더만 복사하지 말고 해당 PC의 설치 위치에서 복원 명령을 실행한다.
원본 URL의 내용이 바뀔 수 있으므로 재다운로드가 과거 모델과 같은 바이트를 보장하지는 않는다.
해시는 각 로컬 복원 시점의 기록이다.
수정한 모델을 정확히 재현하려면 참조 관계를 포함한 별도 백업이 필요하다.

## 실행 확인과 검증 범위

Task 등록과 복원 처리 테스트는 학습이나 물리 시뮬레이션을 실행하지 않는다.
복원 테스트는 작은 임시 USD와 모의 다운로더를 사용하며 실제 모델은 변경하지 않는다.

```bash
env -u PYTHONPATH PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --locked pytest -q
env -u PYTHONPATH uv run --locked python scripts/restore_assets.py --check
env -u PYTHONPATH uv run --locked isaaclab list_envs --show_presets
```

`PYTHONPATH` 제외는 ROS의 Python 3.10 모듈이 Python 3.12 환경에 섞인 문제에 대한 처리이다.
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`은 테스트에 불필요한 외부 플러그인을 읽지 않도록 한다.
ROS 설치 자체는 변경하지 않는다.

위 검사는 GPU 학습, 렌더링, 다른 PC에서의 전체 재설치를 보장하지 않는다.
학습과 재생의 명시적인 실행 명령은 [README](../README.md)에 기록한다.

## GitHub 동기화

작업 브랜치에 소스와 문서만 commit·push하고 Pull Request로 변경을 확인한 뒤 `main`에 반영한다.
초기 태그 `baseline-v0.1.0`은 변경하지 않는다.
모델·로그·체크포인트는 GitHub 소스 백업과 별도로 보관한다.

`.pre-commit-config.yaml`에는 자동 수정이 포함되므로 실행 후 `git diff`를 확인한다.
GitHub Actions를 통한 학습이나 GPU 검증은 아직 설정하지 않았다.

## 공식 근거 자료

- [Isaac Lab External Project 가이드](https://github.com/isaac-sim/IsaacLab/blob/e3f7d9ff1f5d7f8280de3ece9000b7117f66bcf4/docs/source/developer-tools/template_generator.rst)
- [현재 retrieve_file_path 구현](https://github.com/isaac-sim/IsaacLab/blob/e3f7d9ff1f5d7f8280de3ece9000b7117f66bcf4/source/isaaclab/isaaclab/utils/assets.py)
- [OpenUSD 의존 관계 검사 API](https://openusd.org/25.11/api/dependencies_8h.html)
