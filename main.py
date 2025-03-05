import os
import random
import time
from multiprocessing import Process

from constants import HOST, PORTS
from utils import make_folder

from clock import Machine


def run_machine(index):
    """
    Function to start a Machine instance in a separate process.
    """
    tick = random.randint(1, 6)
    machine = Machine(
        id=index + 1,
        port=PORTS[index],
        tick=tick,
        peers=[(HOST, port) for port in PORTS if port != PORTS[index]],
        folder=make_folder(f"{index + 1}"),
    )
    print(f"Machine {index + 1} started with rate {tick} per second.")
    machine.run()


if __name__ == "__main__":
    if not os.path.exists("logs"):
        os.makedirs("logs")

    processes = []

    # start each machine in its own process
    for i in range(3):
        p = Process(target=run_machine, args=(i,))
        p.start()
        processes.append(p)

    try:
        # Let the system run for 80 seconds
        time.sleep(80)
        print("System turning off, jobs complete.")
    except Exception as e:
        print(f"System shutting down because of error: {e}")
    finally:
        # To gracefully stop processes, we would need to modify Machine to check for some external signal,
        # or handle it in the network layer by sending some shutdown signal over sockets.
        # For now, just force terminate all processes.
        for p in processes:
            p.terminate()

        for p in processes:
            p.join()

        print("All processes cleaned up. System shutdown complete.")
