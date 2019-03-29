class MC:
    """
        Mock mc class to simulate crazyflie's motion controller behaviour
    """

    @staticmethod
    def back(s, velocity=0):
        print("mc: back step")

    @staticmethod
    def forward(s, velocity=0):
        print("mc: forward step")

    @staticmethod
    def left(s, velocity=0):
        print("mc: left step")

    @staticmethod
    def right(s, velocity=0):
        print("mc: right step")

    @staticmethod
    def turn_left(s, velocity=0):
        print("mc: turn left")

    @staticmethod
    def turn_right(s, velocity=0):
        print("mc: turn right")