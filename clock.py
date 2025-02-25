from multiprocessing import Queue
import random
import socket
import threading
import time

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

    def send_message(self, peer):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sender:
            try:
                sender.connect(peer)
                with self.lock:
                    self.clock += 1

                msg = f"{self.id}:{self.clock}"
                sender.sendall(msg.encode())

            except:
                print("Machine failed")

    def internal_event(self):
        with self.lock:
            self.clock += 1

    def run(self):
        while self.running:
            # simulate self.tick operations per one second
            time.sleep(1 / self.tick)

            if not self.queue.empty():
                msg = self.queue.get()
                sender, received_clock = msg.split(":")
                received_clock = int(received_clock)
                self.clock = max(self.clock, received_clock) + 1
                print(
                    f"Machine {self.id} received message, received {received_clock}, updated clock to {self.clock}"
                )

            else:
                action = random.choice(["internal", "send"])

                if action == "internal":
                    self.internal_event()
                    print(
                        f"Machine {self.id} internal event, clock updated to {self.clock}"
                    )
                elif action == "send" and self.peers:
                    target = random.choice(self.peers)
                    self.send_message(target)
                    print(f"Machine {self.id} sent message to {target}")

    def stop(self):
        self.running = False
        print(f"Machine {self.id} shutting down.")


if __name__ == "__main__":
    vm1 = Machine(
        1,
        PORTS[0],
        random.randint(1, 6),
        [(HOST, port) for port in PORTS if port != PORTS[0]],
    )
    vm2 = Machine(
        2,
        PORTS[1],
        random.randint(1, 6),
        [(HOST, port) for port in PORTS if port != PORTS[1]],
    )
    vm3 = Machine(
        3,
        PORTS[2],
        random.randint(1, 6),
        [(HOST, port) for port in PORTS if port != PORTS[2]],
    )

    try:
        threading.Thread(target=vm1.run).start()
        threading.Thread(target=vm2.run).start()
        threading.Thread(target=vm3.run).start()
        time.sleep(10)  # let the machines communicate for a while
        print("System turning off, jobs complete.")
    except:
        print("System shutting down because of error.")
    finally:
        vm1.stop()
        vm2.stop()
        vm3.stop()
