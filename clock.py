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
        # the specific id for the VM running
        self.id = id
        # the port in which the VM is running on
        self.port = port
        # the addresses of the other server ports
        self.peers = peers
        # local logical clock of the VM
        self.clock = 0
        # # of clock operations per second
        self.tick = tick

        self.lock = threading.Lock()
        self.queue = Queue()
        self.queue_size = 0
        self.running = True
        self.logger = setup_logger(str(self.id), folder)

        # each virtual machine opens a socket connection to listen for incoming messages on a separate thread
        # so the process is done asynchronously
        self.server_thread = threading.Thread(target=self.listen)
        self.server_thread.daemon = True
        self.server_thread.start()

    def listen(self):
        """
        Creates a client socket for each virtual machine, binding it to the specified port.
        While the VM is running, accepts client connections and creates separate threads for each client connection
        to receive messages.
        """
        # creates a server socket that is binded to the specific port that the VM is on
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as network:
            network.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            network.bind((HOST, self.port))
            network.listen()
            while self.running:
                try:
                    # accepts client connections to the server and feeds the client socket into the receive_messages method
                    # processed with multiple threads so that the VM can receive multiple different connections
                    client, _ = network.accept()
                    threading.Thread(
                        target=self.receive_message, args=(client,)
                    ).start()
                except Exception:
                    break

    def receive_message(self, client):
        """
        Takes in a client socket and decodes the data that is sent over the socket. If there is data,
        append the data to the queue and increment the queue size.
        """
        with client:
            data = client.recv(1024).decode()
            if data:
                with self.lock:
                    # adds the respective data to the queue and increments the size
                    self.queue.put(data)
                    self.queue_size += 1

    def send_message(self, peer):
        """
        Sends a message, taking in a peer that has the address and port of the target VM's server socket. And initiates a connect to
        connect to the target machine's server socket. Increments the local logical clock before the send
        so that the logical clock message accurately reflects the clock time
        """
        # create a new client socket for the VM to send a message through the wire
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
        """
        Simulates an internal event where the local logical clock is simply updated
        """
        with self.lock:
            self.clock += 1

    def run(self):
        """
        Represents the main part of the cycle where the VM processes events self.tick times per second. First it checks
        the message queue to see if there are any updates that need to be made to the logical clock. Then, if the queue
        is empty it randomly generates a number to send to other machines or to send to itself.
        """
        while self.running:
            # simulates the different clock rates for each VM by forcing a pause of 1/self.tick time
            # so that the VM can only perform self.tick operations per second
            time.sleep(1 / self.tick)
            system_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # checks to see if the queue has incoming messages
            if not self.queue.empty():
                with self.lock:
                    msg = self.queue.get()
                    sender, received_clock = msg.split(":")
                    received_clock = int(received_clock)

                    # updating the logical clock with the maximum of either the internal logical clock or the received clock time
                    self.clock = max(self.clock, received_clock) + 1

                    # write in the log that a message from the queue has been received
                    self.logger.info(
                        f"[{system_time}] Machine {self.id} received message from {sender}, "
                        f"Received Clock: {received_clock}, Queue Length: {self.queue_size}, Updated Logical Clock: {self.clock}"
                    )
                    self.queue_size -= 1

            # when there are no messages in the queue we create a randomized action
            else:
                action = random.randint(1, 10)
                if action == 1:
                    # send to one of the other machines a message
                    self.send_message(self.peers[0])

                elif action == 2:
                    # send to the other virtual machine a message
                    self.send_message(self.peers[1])

                elif action == 3:
                    # send to both of the other virtual machines a message
                    self.send_message(self.peers[0])
                    self.send_message(self.peers[1])

                else:
                    # treat the cycle as an internal event
                    self.internal_event()
                    self.logger.info(
                        f"[{system_time}] Machine {self.id} internal event, Updated Logical Clock: {self.clock}"
                    )

    def stop(self):
        """
        Stops the VM from continuously running
        """
        self.running = False
        self.logger.info(f"Machine {self.id} shutting down.")
