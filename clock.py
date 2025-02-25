from multiprocessing import Queue
import random
import socket
import threading

from constants import HOST, PORTS


class Machine:
    def __init__(self, id: int, port: int, tick: int, peers: list):
        self.id = id
        self.port = port
        self.peers = peers
        self.clock = 0
        self.tick = tick
        self.queue = Queue()
        self.running = True

    def listen(self):
        pass

    def handle_connection(self):
        pass

    def send_message(self):
        pass

    def execute_event(self):
        pass

    def run(self):
        pass

    def stop(self):
        pass


if __name__ == "__main__":
    vm1 = Machine(
        1,
        PORTS[0],
        random.randint(1, 6),
        [(HOST, port) for port in PORTS if port != PORTS[0]],
    )
    vm2 = Machine(
        1,
        PORTS[1],
        random.randint(1, 6),
        [(HOST, port) for port in PORTS if port != PORTS[1]],
    )
    vm3 = Machine(
        1,
        PORTS[2],
        random.randint(1, 6),
        [(HOST, port) for port in PORTS if port != PORTS[2]],
    )
