import os
import threading
import time
import logging
import tango
import music
from MC import MC

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander


def handle_beat(flight_time):
    nt = dance.next_task()
    if nt is not None:
        if isinstance(nt, tango.Step):
            length = nt.get_step_size()
            nt.set_velocity(float(length) / (float(flight_time * 3) / 2))
        if isinstance(nt, tango.Wait):
            nt.set_interval(flight_time)
        if isinstance(nt, tango.Turn):
            angle_degrees = nt.get_angle()
            rate = float(angle_degrees) / (float(flight_time * 3) / 2)
            nt.set_rate(rate)
        nt.run()
    else:
        print("beat length: ", flight_time)


if __name__ == '__main__':
    #URI = 'radio://0/80/250K'
    URI = 'radio://0/80/2M'
    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    log = logging.getLogger(__name__)

    cflib.crtp.init_drivers(enable_debug_driver=True)

    simulate = 0

    if simulate:
        dance = tango.pattern(MC, 0.15, 0.9, announce=True)
        dance = tango.pattern(MC, 0.5, 0.9, announce=True)
        music.play("music/LaCumparsita.mp3", handle_beat, 0)
    else:
        with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
            with MotionCommander(scf) as mc:
                mc.up(0.5, velocity=0.3)
                time.sleep(3)
                dance = tango.pattern(mc, 0.15, 0.9, announce=True)
                # dance = TurnFullLeft("TurnFullLeft", mc, 0.5, 0.5, announce=True)
                # dance = tango.dance_tango("Tango", mc, 0.3, 0.9, announce=False)
                t = threading.Thread(target=music.play, args=("music/LaCumparsita.mp3", handle_beat, 0))
                t.start()
                t.join()
                mc.land(0.3)
