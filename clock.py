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
        self.lock = threading.Lock()
        self.queue = Queue()
        self.running = True

    def listen(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as network:
            network.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            network.bind((HOST, self.port))
            network.listen()

            while self.running:
                try:
                    client, _ = network.accept()
                    threading.Thread(
                        target=self.receive_message, args=(client,)
                    ).start()

                except Exception:
                    break

    def receive_message(self, client):
        with client:
            data = client.recv(1024).decode()
            if data:
                received_clock = int(data)
                with self.lock:
                    self.clock = max(self.clock, received_clock) + 1
                    self.queue.put(received_clock)

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
