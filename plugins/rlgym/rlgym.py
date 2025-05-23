import logging
from typing import Any

import gymnasium as gym
from bluesky import core, stack
from gymnasium import Env

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
        self._env: Env | None = None

    @core.timed_function(name="rlloop", dt=5)
    def update(self) -> None:
        if not self._env:
            return

        # TODO move this into control of the gym lib.
        # There, provide the possibility to attach RL algorithms.
        action = self._env.action_space.sample()
        observation, reward, terminated, truncated, info = self._env.step(action)
        if terminated or truncated:
            self._env.reset()

    @stack.command
    def train(self, environment=None):
        if environment is None:
            if self._env:
                self._env.close()
                self._env = None
        else:
            self._env = gym.make(
                f"bluesky_gym/{gym}",
                time_step=5,
            )
            self._env.reset()
        return True, f"Training in the gym is {'dis' if self._env is None else 'en'}abled."