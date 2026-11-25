# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Tests for the project's task registrations."""

import gymnasium as gym
import pytest

import go2_locomotion.tasks  # noqa: F401


@pytest.mark.parametrize("terrain", ["Flat", "Rough"])
def test_task_registrations(terrain):
    """Each research task must resolve to the project-owned environment and PPO configuration."""
    spec = gym.spec(f"Research-Go2-{terrain}")
    package = "go2_locomotion.tasks.locomotion.config.go2"
    assert spec.entry_point == "isaaclab.envs:ManagerBasedRLEnv"
    assert spec.kwargs["env_cfg_entry_point"] == f"{package}.{terrain.lower()}_env_cfg:Go2{terrain}EnvCfg"
    assert spec.kwargs["rsl_rl_cfg_entry_point"] == f"{package}.agents.rsl_rl_ppo_cfg:Go2{terrain}PPORunnerCfg"
    assert spec.kwargs["default_agent"] == "rsl_rl"
