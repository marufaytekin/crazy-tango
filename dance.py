import os
from time import sleep

from tango import *
from MC import MC

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander

log = logging.getLogger(__name__)


def pattern(_mc, step_size=0.0, velocity=1.0, *args, **kwargs):
    forward = Step("forward", _mc, step_size, velocity, Direction.FORWARD, *args, **kwargs)
    backward = Step("backward", _mc, step_size, velocity, Direction.BACK, *args, **kwargs)
    left = Step("left", _mc, step_size, velocity, Direction.LEFT, *args, **kwargs)
    right = Step("right", _mc, step_size, velocity, Direction.RIGHT, *args, **kwargs)
    collect = Wait("collect", float(step_size / velocity), *args, **kwargs)

    p = Sequence("Tango")
    p.add_child(forward)
    p.add_child(backward)
    p.add_child(left)
    p.add_child(right)
    p.add_child(collect)

    return p


if __name__ == '__main__':
    URI = 'radio://0/80/250K'
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
    cflib.crtp.init_drivers(enable_debug_driver=True)

    simulate = 1

    if simulate:
        dance = pattern(MC, 0.5, 0.9, announce=True)
        # dance = dance_tango("Tango", MC, 0.5, 0.9, announce=True)
        step = dance.next_move()
        while step:
            status = step.run()
            if status == TaskStatus.SUCCESS:
                print("SUCCESS")
            sleep(2)
            step = dance.next_move()
    else:
        with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
            with MotionCommander(scf) as mc:
                mc.up(0.5, velocity=0.5)
                time.sleep(3)
                dance = pattern(mc)
                dance.run()
                mc.land(0.5)
