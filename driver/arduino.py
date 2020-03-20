import time
from pyfirmata import Arduino, util


class ArduinoUno:
    def __init__(self, port=None):
        if port is None:
            port = "COM3"
        self.port = port

    def board(self):
        board = Arduino(self.port)
        return board

    def iterative_move(self):
        iterator = util.Iterator(self.board)
        iterator.start()
        time.sleep(1.0)
