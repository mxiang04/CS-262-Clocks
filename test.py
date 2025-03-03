import datetime
import unittest
import os
import threading
import time
import shutil
import random
from clock import Machine
from utils import make_folder
from constants import HOST, PORTS


class TestLogicalClocks(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up logs directory before all tests."""
        cls.clean_logs()
        os.makedirs("logs", exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        """Clean up logs after all tests."""
        cls.clean_logs()

    @classmethod
    def clean_logs(cls):
        """Helper to clear log directories."""
        if os.path.exists("logs"):
            shutil.rmtree("logs")

    def setUp(self):
        """Set up 3 machines for testing."""
        self.VMs = []
        clock_range_max = 3

        for index in range(3):
            tick = random.randint(1, clock_range_max)
            machine = Machine(
                id=index + 1,
                port=PORTS[index],
                tick=tick,
                peers=[(HOST, port) for port in PORTS if port != PORTS[index]],
                folder=make_folder(f"{index + 1}"),
            )
            self.VMs.append(machine)

        self.vm_threads = [threading.Thread(target=vm.run) for vm in self.VMs]

    def tearDown(self):
        """Stop all VMs and wait for threads to close."""
        for vm in self.VMs:
            vm.stop()

        for thread in self.vm_threads:
            thread.join()

    def test_machines_run_and_log(self):
        """
        Verify that machines run, generate logs, and shut down cleanly.
        """
        # start the machines
        for thread in self.vm_threads:
            thread.start()

        # let the machines run for a bit
        time.sleep(5)

        # check that each machine has created a non-empty log file
        for index in range(1, 4):
            log_folder = f"logs/{datetime.datetime.now().strftime('%m_%d_%y_%H:%M')}"
            log_file = f"{log_folder}/machine{index}.log"
            self.assertTrue(
                os.path.exists(log_file), f"Log file {log_file} does not exist"
            )

            with open(log_file, "r") as file:
                log_contents = file.read().strip()

            self.assertGreater(len(log_contents), 0, f"Log file {log_file} is empty")

        print("Machines ran, logged, and shut down cleanly.")


if __name__ == "__main__":
    unittest.main()
