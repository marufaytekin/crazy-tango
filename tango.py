from enum import Enum
from tasks import *


class Direction(Enum):
    BACK = 0
    FORWARD = 1
    LEFT = 2
    RIGHT = 3


class Step(Task):

    def __init__(self, name, mc, step_size, velocity, direction, *args, **kwargs):
        super(Step, self).__init__(name, *args, **kwargs)
        self.step_size = step_size
        self.velocity = velocity
        self.direction = direction
        self.mc = mc

    def run(self):
        if self._announce:
            self.announce()
        try:
            if self.direction == Direction.BACK:
                self.mc.back(self.step_size, velocity=self.velocity)
            elif self.direction == Direction.FORWARD:
                self.mc.forward(self.step_size, velocity=self.velocity)
            elif self.direction == Direction.LEFT:
                self.mc.left(self.step_size, velocity=self.velocity)
            elif self.direction == Direction.RIGHT:
                self.mc.right(self.step_size, velocity=self.velocity)
            return TaskStatus.SUCCESS
        except Exception as e:
            log.error(e)
            return TaskStatus.FAILURE


class Turn(Task):

    def __init__(self, name, mc, angle_degrees, rate, direction, *args, **kwargs):
        super(Turn, self).__init__(name, *args, **kwargs)
        self.angle_degrees = angle_degrees
        self.rate = rate
        self.direction = direction
        self.mc = mc

    def run(self):
        if self._announce:
            self.announce()
        try:
            if self.direction == Direction.LEFT:
                self.mc.turn_left(self.angle_degrees, self.rate)
            elif self.direction == Direction.RIGHT:
                self.mc.turn_right(self.angle_degrees, self.rate)
            return TaskStatus.SUCCESS
        except Exception as e:
            log.error(e)
            return TaskStatus.FAILURE


class BoxStep(Sequence):

    def __init__(self, name, mc, step_size, velocity, *args, **kwargs):
        super(BoxStep, self).__init__(name, *args, **kwargs)

        forward = Step("forward", mc, step_size, velocity, Direction.FORWARD, *args, **kwargs)
        backward = Step("backward", mc, step_size, velocity, Direction.BACK, *args, **kwargs)
        left = Step("left", mc, step_size, velocity, Direction.LEFT, *args, **kwargs)
        right = Step("right", mc, step_size, velocity, Direction.RIGHT, *args, **kwargs)
        collect = Wait("collect", float(step_size / velocity), *args, **kwargs)  # beat_time = step_size / velocity

        self.add_child(forward)
        self.add_child(right)
        self.add_child(collect)
        self.add_child(backward)
        self.add_child(left)
        self.add_child(collect)


class EightSteps(Sequence):

    def __init__(self, name, mc, step_size, velocity, *args, **kwargs):
        super(EightSteps, self).__init__(name, *args, **kwargs)

        forward = Step("forward", mc, step_size, velocity, Direction.FORWARD, *args, **kwargs)
        backward = Step("backward", mc, step_size, velocity, Direction.BACK, *args, **kwargs)
        left = Step("left", mc, step_size, velocity, Direction.LEFT, *args, **kwargs)
        right = Step("right", mc, step_size, velocity, Direction.RIGHT, *args, **kwargs)
        collect = Wait("collect", float(step_size / velocity), *args, **kwargs)  # beat_time = step_size / velocity

        self.add_child(backward)
        self.add_child(left)
        self.add_child(forward)
        self.add_child(forward)
        self.add_child(collect)
        self.add_child(forward)
        self.add_child(right)
        self.add_child(collect)


class OchoCortado(Sequence):

    def __init__(self, name, mc, step_size, velocity, *args, **kwargs):
        super(OchoCortado, self).__init__(name, *args, **kwargs)

        forward = Step("forward", mc, step_size / 2, velocity, Direction.FORWARD, *args, **kwargs)
        skip_beat = Wait("Skip Beat", float(step_size / velocity), *args, **kwargs)  # beat_time = step_size / velocity
        turn_right = Turn("Turn Right", mc, 45, 360, Direction.RIGHT, *args, **kwargs)
        turn_half_right = Turn("Turn Right", mc, 25, 360, Direction.RIGHT, *args, **kwargs)
        turn_half_left = Turn("Turn Left", mc, 25, 360, Direction.LEFT, *args, **kwargs)

        self.add_child(forward)
        self.add_child(turn_right)
        self.add_child(skip_beat)
        self.add_child(turn_half_right)
        self.add_child(turn_half_left)
        self.add_child(skip_beat)


class OchoCortadoLinear(Sequence):

    def __init__(self, name, mc, step_size, velocity, *args, **kwargs):
        super(OchoCortadoLinear, self).__init__(name, *args, **kwargs)

        backward = Step("backward", mc, step_size, velocity, Direction.BACK, *args, **kwargs)
        skip_beat = Wait("Skip Beat", float(step_size / velocity), *args, **kwargs)  # beat_time = step_size / velocity
        turn_right = Turn("Turn Right", mc, 45, 360, Direction.RIGHT, *args, **kwargs)
        turn_left = Turn("Turn Right", mc, 45, 360, Direction.LEFT, *args, **kwargs)
        uncross_back = Turn("Uncross Back", mc, 20, 360, Direction.LEFT, *args, **kwargs)

        self.add_child(uncross_back)
        self.add_child(backward)
        self.add_child(turn_right)
        self.add_child(turn_left)
        self.add_child(skip_beat)


def dance_tango(name, mc, step_size, velocity, *args, **kwargs):

    behave = Sequence(name)
    forward = Step("forward", mc, step_size, velocity, Direction.FORWARD, *args, **kwargs)
    skip_beat = Wait("Skip Beat", float(step_size / velocity), *args, **kwargs)  # beat_time = step_size / velocity
    turn_right = Turn("Turn Right", mc, 45, 360, Direction.RIGHT, *args, **kwargs)
    turn_left = Turn("Turn Left", mc, 45, 360, Direction.LEFT, *args, **kwargs)
    turn_half_right = Turn("Turn Right", mc, 25, 360, Direction.RIGHT, *args, **kwargs)
    turn_half_left = Turn("Turn Left", mc, 25, 360, Direction.LEFT, *args, **kwargs)
    box = BoxStep("BoxStep", mc, step_size, velocity, *args, **kwargs)
    ocho_cordato = OchoCortado("OchoCortado", mc, step_size, velocity, *args, **kwargs)
    ocho_cordato_linear = OchoCortadoLinear("OchoCortadoLinear", mc, step_size, velocity, *args, **kwargs)
    eight_steps = EightSteps("EightSteps", mc, step_size, velocity, *args, **kwargs)

    behave.add_child(box)
    behave.add_child(skip_beat)
    behave.add_child(forward)
    behave.add_child(forward)
    behave.add_child(skip_beat)
    behave.add_child(ocho_cordato_linear)
    behave.add_child(forward)
    behave.add_child(eight_steps)
    behave.add_child(forward)
    behave.add_child(ocho_cordato_linear)
    behave.add_child(turn_half_left)
    behave.add_child(forward)
    behave.add_child(ocho_cordato)
    behave.add_child(turn_left)
    behave.add_child(forward)
    behave.add_child(ocho_cordato)
    behave.add_child(turn_half_left)
    behave.add_child(turn_half_left)
    behave.add_child(turn_half_left)
    behave.add_child(forward)

    return behave
