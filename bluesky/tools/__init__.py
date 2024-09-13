''' BlueSky tools. '''
import bluesky as bs


def init():
    import bluesky.tools.geo as geo
    bs.logger.info("Reading magnetic variation data")
    geo.initdecl_data()
