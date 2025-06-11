import numpy as np
from bluesky import core, stack, traf  # , settings, navdb, sim, scr, tools


def init_plugin():
    """Plugin initialisation function."""
    # Instantiate our example entity
    Groundops()

    # Configuration parameters
    config = {
        # The name of your plugin
        "plugin_name": "GROUNDOPS",
        # The type of this plugin. For now, only simulation plugins are possible.
        "plugin_type": "sim",
    }

    # init_plugin() should always return a configuration dict.
    return config


class Groundops(core.Entity):
    def __init__(self):
        super().__init__()
        # All classes deriving from Entity can register lists and numpy arrays
        # that hold per-aircraft data. This way, their size is automatically
        # updated when aircraft are created or deleted in the simulation.
        with self.settrafarrays():
            self.is_in_pushback = np.array([])
            self.pb_initial_heading = np.array([])
            self.pb_pushback_dist = np.array([])

    @core.timed_function
    def update(self):
        pbs = np.argwhere(self.is_in_pushback)
        # this does not work --> implement own "physics" and use move?
        # traf.selspd[pbs] = -20
        pass

    @stack.command
    def pushback(
        self, acid: "acid", distance: float | None = None, direction: int | None = None
    ):
        if distance is None or direction is None:
            return (
                True,
                f"Aircraft {traf.id[acid]} currently does "
                f"{'not ' if not self.is_in_pushback[acid] else ''}perform pushback.",
            )

        self.is_in_pushback[acid] = True
        self.pb_initial_heading[acid] = traf.hdg[acid]
        self.pb_pushback_dist[acid] = 0
        return True, f"Pushback initiaeted for aircraft {acid}."
