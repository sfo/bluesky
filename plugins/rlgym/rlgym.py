import logging
from typing import Any, override

import gymnasium as gym
import numpy as np
from bluesky import core, sim, stack, traf
from bluesky_gym.envs import BlueSkyEnv
from gymnasium import registry

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Initialization function of the plugin as required by BlueSky to identify it.
def init_plugin() -> dict[str, Any]:
    BlueSkyGym()
    return {
        "plugin_name": "BlueSky Gym",
        "plugin_type": "sim",
    }


class BlueSkyGym(core.Entity):
    def __init__(self) -> None:
        super().__init__()
        logger.info("Welcome to the Gym!")
        self._env: BlueSkyEnv | None = None
        self._observation: dict | None = None
        self._last_radar_update = -np.inf
        self._action_duration = None

    @core.timed_function(name="rl_action", hook="preupdate")
    def perform_action(self) -> None:
        if self._env is None or self._observation is None:
            return

        if sim.simt - self._last_radar_update < 5:  # TODO - move this to the environment to allow it to decide for the time step to use
            self._action_duration = None
            return

        logger.info(f"Radar updated at {sim.simt}. Performing Action!")
        self._last_radar_update = sim.simt

        # TODO - call the library (aka the "agent") to decide which algorithm to use for
        # selecting an action
        action = self._env.action_space.sample()
        self._action_duration = self._env.perform_action(action)

    # in between preupdate and update hook, the simulation kicks in and updates traffic.

    @core.timed_function(name="rl_reward", hook="update")
    def collect_reward_and_observation(self) -> None:
        if self._env is None:
            return

        if self._action_duration is None:
            return

        logger.info(f"Collecting rewards and obtain new observation at {sim.simt}.")

        self._observation = self._env.get_observation()
        terminated, final_reward = self._env._terminated()
        if terminated:
            logger.info("Environment terminated.")
        # reward = final_reward - action_duration  # penalty for each action is equal to
        # its duration
        truncated = self._env._truncated()
        if truncated:
            logger.info("Environment truncated.")
        # info = {}
        if terminated or truncated:
            logger.info("Resetting the traffic object and environment")
            # official bs gym environment does not reset the full simulation, but instead does:
            # this call could be part of env.reset, since it is the same for all render_modes.
            traf.reset()  # this calls reset of all the TrafficArray classes (also this one), so no need to self.reset
            # self._observation, _ = self._env.reset()
            # self._last_radar_update = -np.inf
            # # self.reset()

    @stack.command
    def train(self, environment: str | None = None, algorithm: str | None = None):
        if environment is None:
            if self._env:
                self._env.close()
                self._env = None
            else:
                return (
                    True,
                    f"Environments available: {
                        [
                            env
                            for env in registry
                            if env.startswith('bluesky_gym/')
                        ]
                    }",
                )
        else:
            self._env = gym.make(
                f"bluesky_gym/{environment}",
                render_mode="plugin",
                time_step=5,
            )  # type: ignore
            self._observation, _ = self._env.reset()
            self._last_radar_update = -np.inf
        return (
            True,
            f"Training in the gym is {'dis' if self._env is None else 'en'}abled.",
        )

    @override
    def reset(self) -> None:
        logger.info("Resetting the Gym.")
        if self._env is not None:
            self._last_radar_update = -np.inf
            self._action_duration = None
            self._observation, _ = self._env.reset()
