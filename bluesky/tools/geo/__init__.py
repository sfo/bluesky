''' BlueSky functions for geographical calculations. '''
import bluesky as bs
from bluesky import settings
from bluesky.tools.geo._geo import nm, magdec, initdecl_data, magdeccmd, kwikpos


# Register settings defaults
settings.set_variable_defaults(prefer_compiled=False)
if getattr(settings, 'prefer_compiled'):
    try:
        from bluesky.tools.geo._cgeo import (
            rwgs84,
            rwgs84_matrix,
            qdrdist,
            qdrdist_matrix,
            latlondist,
            latlondist_matrix,
            wgsg,
            qdrpos,
            kwikdist,
            kwikdist_matrix,
            kwikqdrdist,
            kwikqdrdist_matrix
        )
        bs.logger.info('Using compiled geo functions')
    except ImportError:
        from bluesky.tools.geo._geo import (rwgs84, rwgs84_matrix, qdrdist,
                                        qdrdist_matrix, latlondist, latlondist_matrix,
                                        wgsg, qdrpos, kwikdist, kwikdist_matrix,
                                        kwikqdrdist, kwikqdrdist_matrix)
        bs.logger.info('Could not load compiled geo functions, Using Python-based geo functions instead')
else:
    from bluesky.tools.geo._geo import (rwgs84, rwgs84_matrix, qdrdist,
                                        qdrdist_matrix, latlondist, latlondist_matrix,
                                        wgsg, qdrpos, kwikdist, kwikdist_matrix,
                                        kwikqdrdist, kwikqdrdist_matrix)
    bs.logger.info('Using Python-based geo functions')