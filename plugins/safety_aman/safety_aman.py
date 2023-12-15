""" BlueSky plugin template. The text you put here will be visible
    in BlueSky as the description of your plugin. """
from random import randint
import numpy as np
# Import the global bluesky objects. Uncomment the ones you need
from bluesky import core, stack, traf  #, settings, navdb, sim, scr, tools

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('S-AMAN')


### Initialization function of your plugin. Do not change the name of this
### function, as it is the way BlueSky recognises this file as a plugin.
def init_plugin():
    ''' Plugin initialisation function. '''
    # Instantiate our example entity
    SafetyAMAN()

    # Configuration parameters
    config = {
        # The name of your plugin
        'plugin_name':     'SAFETY AMAN',

        # The type of this plugin. For now, only simulation plugins are possible.
        'plugin_type':     'sim',
        }

    # init_plugin() should always return a configuration dict.
    return config


### Entities in BlueSky are objects that are created only once (called singleton)
### which implement some traffic or other simulation functionality.
### To define an entity that ADDS functionality to BlueSky, create a class that
### inherits from bluesky.core.Entity.
### To replace existing functionality in BlueSky, inherit from the class that
### provides the original implementation (see for example the asas/eby plugin).
class SafetyAMAN(core.Entity):
    ''' Example new entity object for BlueSky. '''
    def __init__(self):
        super().__init__()
        # All classes deriving from Entity can register lists and numpy arrays
        # that hold per-aircraft data. This way, their size is automatically
        # updated when aircraft are created or deleted in the simulation.
        logger.info("Hello, Bluesky!")
        self._enabled = False

    def create(self, n=1):
        ''' This function gets called automatically when new aircraft are created. '''

        # Don't forget to call the base class create when you reimplement this function!
        super().create(n)

        # After base creation we can change the values in our own states for the new aircraft
        logger.info(f"Hello, new aircraft!")

    # Functions that need to be called periodically can be indicated to BlueSky
    # with the timed_function decorator
    @core.timed_function(name='control', dt=5)
    def update(self):
        ''' Periodic update function for our example entity. '''

        if traf.ntraf < 1 or not self._enabled:
            return

        logger.info("Assigning random actions to random aircraft")
        acidx = randint(0, traf.ntraf-1)
        acid = traf.id[acidx]

        altitude = randint(1500, 5000)
        cmdstr = 'ALT %s, %f' % (acid,  altitude)
        stack.stack(cmdstr)

        heading = randint(0, 360)
        cmdstr = 'HDG %s, %f' % (acid,  heading)
        stack.stack(cmdstr)

        speed = randint(150, 250)
        cmdstr = 'SPD %s, %f' % (acid,  speed)
        stack.stack(cmdstr)

    # You can create new stack commands with the stack.command decorator.
    # By default, the stack command name is set to the function name.
    # The default argument type is a case-sensitive word. You can indicate different
    # types using argument annotations. This is done in the below function:
    # - The acid argument is a BlueSky-specific argument with type 'acid'.
    #       This converts callsign to the corresponding index in the traffic arrays.
    # - The count argument is a regular int.
    @stack.command
    def saman(self, enable=None):
        if enable is None:
            return True, f'S-AMAN supported air traffic control is {"enabled" if self._enabled else "disabled"}.'
        self._enabled = enable
        return True, f'{"enabled" if enable else "disabled"} S-AMAN supported air traffic control.'
