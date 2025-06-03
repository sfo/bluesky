import logging
from typing import Any, override

import gymnasium as gym
import numpy as np
from bluesky import core, sim, stack, traf
from bluesky_gym.envs import BlueSkyEnv
from gymnasium import registry

logging.basicConfig(level=logging.DEBUG)  # FIXME - this should not happen in the plugin
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
        if self._env is None:
            logger.debug("No environment initialized. Cannot perform action.")
            return

        if  self._observation is None:
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

    @core.timed_function(name="rl_reward", hook="update")
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

        # FIXME - this should propably be handled during action, so agent can react on final reward
        if terminated or truncated:
            logger.debug("Environment terminated or truncated. Resetting the traffic object")
            # this calls reset of all the TrafficArray classes (also this one), so no need to self.reset
            traf.reset()

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
                radar_update_rate=5,
            )  # type: ignore
            self.reset_environment()
        return (
            True,
            f"Training in the gym is {'dis' if self._env is None else 'en'}abled.",
        )

    def reset_environment(self) -> None:
        logger.debug("Resetting the environment.")
        self._observation, _ = self._env.reset()
        self._last_radar_update = -np.inf
        self._action_duration = None

    @override
    def reset(self) -> None:
        logger.info("Resetting the Gym.")
        if self._env is not None:
            self.reset_environment()
