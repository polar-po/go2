"""Go2 flat-terrain locomotion environment."""

from isaaclab.utils import configclass, replace

from isaaclab_tasks.core.velocity.config.go2.flat_env_cfg import (
    UnitreeGo2FlatEnvCfg,
)

from go2_locomotion.assets.go2_cfg import GO2_CFG


@configclass
class Go2FlatEnvCfg(UnitreeGo2FlatEnvCfg):

    def __post_init__(self):
        super().__post_init__()

        # Use the project-owned robot configuration.
        self.scene.robot = replace(
            GO2_CFG,
            prim_path="{ENV_REGEX_NS}/Robot",
        )
