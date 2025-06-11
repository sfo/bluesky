import logging
from typing import Any

import gymnasium as gym
import numpy as np
from bluesky import sim, stack
from bluesky.core import Base
from bluesky.core.timedfunction import timed_function
from bluesky_gym.envs import BlueSkyEnv
from gymnasium import registry
from gymnasium.core import ObsType

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


__gym = None


# Initialization function of the plugin as required by BlueSky to identify it.
def init_plugin() -> dict[str, Any]:
    global __gym
    __gym = BlueSkyGym()
    return {
        "plugin_name": "BlueSky Gym",
        "plugin_type": "sim",
        "reset": __gym.reset_gym,
    }


class BlueSkyGym(Base):
    def __init__(self) -> None:
        super().__init__()
        logger.info("Welcome to the Gym!")
        self._env: BlueSkyEnv | None = None
        self._observation: ObsType | None = None  # type: ignore
        self._last_radar_update = -np.inf
        self._action_duration = None

    @timed_function(name="rl_action", hook="preupdate")
    def perform_action(self) -> None:
        if self._env is None:
            logger.debug("No environment initialized. Cannot perform action.")
            return

        if self._observation is None:
            logger.debug("No new observation. Cannot perform action.")
            return

        # TODO - call the library (aka the "agent") to decide which algorithm to use for
        # selecting an action
        logger.info(f"Radar updated at {sim.simt}. Performing Action!")
        # consume observation
        self._observation = None

        self._last_radar_update = sim.simt
        action = self._env.action_space.sample()
        self._action_duration = self._env.perform_action(action)

    # in between preupdate and update hook, the simulation kicks in and updates traffic.

    @timed_function(name="rl_reward", hook="update")
    def collect_reward_and_observation(self) -> None:
        if self._env is None:
            logger.debug("No environment initialized. Cannot collect rewards.")
            return

        if self._action_duration is None:
            logger.debug("No previous action for which to collect rewards.")
            return

        if sim.simt - self._last_radar_update < np.maximum(5, self._action_duration):
            # TODO - this may confuse Agents. May be better implement radar update
            # interval in simulation, so the environment only returns on actual updates.
            # Alternatively, try around with DT settings.
            logger.debug("Will not evaluate action, yet.")
            return

        logger.info(f"Collecting rewards and obtain new observation at {sim.simt}.")

        self._observation = self._env._observation
        terminated, final_reward = self._env._terminated
        truncated, penalty = self._env._truncated

        reward = final_reward - self._action_duration - penalty
        info = {}

        # FIXME - should be handled during action, so agent can react on final reward
        if terminated or truncated:
            logger.debug("Resetting the traffic object")
            self.reset_environment()

    @stack.command
    def train(self, environment: str | None = None, algorithm: str | None = None):
        if (environment is None) ^ (algorithm is None):
            return True, "Error: Missing environment or algorithm!"

        if environment is None:
            if self._env:
                self.reset_gym()
            else:
                environments = "\n- ".join(
                    [""] + [env for env in registry if env.startswith("bluesky_gym/")]
                )
                return (
                    True,
                    f"Environments available: {environments}",
                )
        else:
            self._env = gym.make(
                f"bluesky_gym/{environment}",
                render_mode="plugin",
                radar_update_rate=5,
            )  # type: ignore
            self.reset_environment()
        return (
            True,
            f"Training in the gym is {'dis' if self._env is None else 'en'}abled.",
        )

    def reset_environment(self) -> None:
        logger.debug("Resetting the environment.")
        assert self._env is not None
        self._observation, _ = self._env.reset()
        self._last_radar_update = -np.inf
        self._action_duration = None

    def reset_gym(self) -> None:
        logger.info("Resetting the Gym.")
        if self._env is not None:
            self._env.close()
        self._env = None
