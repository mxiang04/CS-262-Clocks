import datetime
from multiprocessing import Queue
import os
import random
import socket
import threading
import time

from constants import HOST, PORTS
from utils import make_folder, setup_logger


class Machine:
    def __init__(self, id: int, port: int, tick: int, peers: list, folder):
        self.id = id
        self.port = port
        self.peers = peers
        self.clock = 0
        self.tick = tick
        self.lock = threading.Lock()
        self.queue = Queue()
        self.queue_size = 0
        self.running = True
        self.logger = setup_logger(str(self.id), folder)

        self.server_thread = threading.Thread(target=self.listen)
        self.server_thread.daemon = True
        self.server_thread.start()

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
                with self.lock:
                    self.queue.put(data)
                    self.queue_size += 1

    def send_message(self, peer):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sender:
            try:
                sender.connect(peer)
                with self.lock:
                    self.clock += 1

                msg = f"{self.id}:{self.clock}"
                sender.sendall(msg.encode())

                # log send event with system time
                system_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.logger.info(
                    f"[{system_time}] Machine {self.id} sent message to {peer}, Logical Clock: {self.clock}"
                )

            except:
                self.logger.error(f"Machine {self.id} failed to send message to {peer}")

    def internal_event(self):
        with self.lock:
            self.clock += 1

    def run(self):
        while self.running:
            time.sleep(1 / self.tick)  # simulate self.tick operations per second
            system_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if not self.queue.empty():
                with self.lock:
                    msg = self.queue.get()
                    sender, received_clock = msg.split(":")
                    received_clock = int(received_clock)
                    self.clock = max(self.clock, received_clock) + 1
                    self.logger.info(
                        f"[{system_time}] Machine {self.id} received message from {sender}, "
                        f"Received Clock: {received_clock}, Queue Length: {self.queue_size}, Updated Logical Clock: {self.clock}"
                    )
                    self.queue_size -= 1

            else:
                action = random.randint(1, 10)
                if action == 1:
                    self.send_message(self.peers[0])

                elif action == 2:
                    self.send_message(self.peers[1])

                elif action == 3:
                    self.send_message(self.peers[0])
                    self.send_message(self.peers[1])

                else:
                    self.internal_event()
                    self.logger.info(
                        f"[{system_time}] Machine {self.id} internal event, Updated Logical Clock: {self.clock}"
                    )

    def stop(self):
        self.running = False
        self.logger.info(f"Machine {self.id} shutting down.")


if __name__ == "__main__":
    if not os.path.exists("logs"):
        os.makedirs("logs")

    vm1 = Machine(
        1,
        PORTS[0],
        random.randint(1, 6),
        [(HOST, port) for port in PORTS if port != PORTS[0]],
        make_folder("1"),
    )
    vm2 = Machine(
        2,
        PORTS[1],
        random.randint(1, 6),
        [(HOST, port) for port in PORTS if port != PORTS[1]],
        make_folder("2"),
    )
    vm3 = Machine(
        3,
        PORTS[2],
        random.randint(1, 6),
        [(HOST, port) for port in PORTS if port != PORTS[2]],
        make_folder("3"),
    )

    try:
        threading.Thread(target=vm1.run).start()
        threading.Thread(target=vm2.run).start()
        threading.Thread(target=vm3.run).start()
        time.sleep(60)  # let the machines communicate for a while
        print("System turning off, jobs complete.")
    except:
        print("System shutting down because of error.")
    finally:
        vm1.stop()
        vm2.stop()
        vm3.stop()
