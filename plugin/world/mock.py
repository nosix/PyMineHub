__all__ = [
    'GPIO'
]


class GPIOMock:

    BOARD = 0
    OUT = 0
    IN = 0
    HIGH = 0
    LOW = 0

    def setmode(self, mode):
        pass

    def setup(self, channel, state):
        pass

    # noinspection PyMethodMayBeStatic
    def input(self, channel) -> bool:
        return channel % 2 == 0

    def output(self, channel, outmode):
        pass


GPIO = GPIOMock()
