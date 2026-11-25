"""RSL-RL PPO configurations for Go2 locomotion."""

from isaaclab.utils import configclass

from isaaclab_tasks.core.velocity.config.go2.agents.rsl_rl_ppo_cfg import (
    UnitreeGo2FlatPPORunnerCfg,
    UnitreeGo2RoughPPORunnerCfg,
)


@configclass
class Go2FlatPPORunnerCfg(UnitreeGo2FlatPPORunnerCfg):

    def __post_init__(self):
        super().__post_init__()

        self.experiment_name = "go2_flat"


@configclass
class Go2RoughPPORunnerCfg(UnitreeGo2RoughPPORunnerCfg):

    def __post_init__(self):
        super().__post_init__()

        self.experiment_name = "go2_rough"
