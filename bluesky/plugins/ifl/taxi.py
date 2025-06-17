from typing import override

from bluesky import core, logger, stack
from bluesky.traffic.performance.openap.perfoap import OpenAP


def init_plugin():
    config = {
        "plugin_name": "TAXIPERF",
        "plugin_type": "sim",
    }
    return config


class TaxiPerf(OpenAP):
    @override
    def calc_axmax(self):
        logger.info("Inside TAXI plugin")
        return super().calc_axmax()