"""Reusable and project-specific MDP terms."""

# Reward functions
from isaaclab_tasks.core.velocity.mdp import (
    track_lin_vel_xy_exp,
    track_ang_vel_z_exp,
    lin_vel_z_l2,
    ang_vel_xy_l2,
    joint_torques_l2,
    joint_acc_l2,
    action_rate_l2,
    feet_air_time,
    undesired_contacts,
    flat_orientation_l2,
    joint_pos_limits,
    base_height_l2,
)

# Observation functions
from isaaclab_tasks.core.velocity.mdp import (
    base_lin_vel,
    base_ang_vel,
    projected_gravity,
    generated_commands,
    joint_pos_rel,
    joint_vel_rel,
    last_action,
    height_scan,
)

# Actions
from isaaclab_tasks.core.velocity.mdp import (
    JointPositionActionCfg,
)

# Commands
from isaaclab_tasks.core.velocity.mdp import (
    UniformVelocityCommandCfg,
)

# Events and domain randomization
from isaaclab_tasks.core.velocity.mdp import (
    randomize_rigid_body_material,
    randomize_rigid_body_mass,
    randomize_rigid_body_com,
    apply_external_force_torque,
    reset_root_state_uniform,
    reset_joints_by_scale,
    push_by_setting_velocity,
)

# Terminations
from isaaclab_tasks.core.velocity.mdp import (
    time_out,
    illegal_contact,
)

# Curriculum
from isaaclab_tasks.core.velocity.mdp import (
    terrain_levels_vel,
)
