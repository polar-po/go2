"""Go2 locomotion task registrations."""

import gymnasium as gym


gym.register(
    id="Research-Go2-Flat",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point":
            f"{__name__}.flat_env_cfg:Go2FlatEnvCfg",
        "rsl_rl_cfg_entry_point":
            f"{__name__}.agents.rsl_rl_ppo_cfg:Go2FlatPPORunnerCfg",
        "default_agent": "rsl_rl",
    },
)


gym.register(
    id="Research-Go2-Rough",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point":
            f"{__name__}.rough_env_cfg:Go2RoughEnvCfg",
        "rsl_rl_cfg_entry_point":
            f"{__name__}.agents.rsl_rl_ppo_cfg:Go2RoughPPORunnerCfg",
        "default_agent": "rsl_rl",
    },
)
