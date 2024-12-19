import math
import time

import pyagxrobots


class Robot:
    def __init__(self, demo=False):
        self.demo = demo
        if not demo:
            self.scoutmini = pyagxrobots.pysdkugv.ScoutMiniBase()
            self.scoutmini.EnableCAN()

    def rotate(self, angle, speed=0.25, calibration=0.875):
        if self.demo:
            print(f"rotate by {angle}")
            return

        rotation_time = abs(angle) * calibration / speed
        if angle < 0:
            speed *= -1
        start = time.time()
        while rotation_time > time.time() - start:
            self.scoutmini.SetMotionCommand(angular_vel=speed)


if __name__ == "__main__":
    robot = Robot()
    robot.rotate(2 * math.pi, speed=0.25)
