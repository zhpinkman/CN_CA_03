import threading
import time
from pathlib import Path
import json

from Hello import Hello

RESULT_FOLDER = "RESULTS"


class Logger:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.current_bidirectional_neighbors = []
        self.nodes_available_time = dict()
        self.destroy = False

        self.timer_thread = threading.Thread(target=self.logger_timer_task, name='LOGGER_TIMER_TASK')
        self.timer_thread.start()

    def terminate(self, overall_time_in_seconds):
        self.destroy = True
        self.wrap_up(overall_time_in_seconds)

    def wrap_up(self, overall_time_in_seconds):
        self.wrap_up_3_available_time()

    def wrap_up_3_available_time(self):
        path = RESULT_FOLDER + "/" + str(self.ip) + "_" + str(self.port)
        Path(path).mkdir(parents=True, exist_ok=True)
        with open(path + "/3_available_time_in_seconds.json", "w") as available_file:
            available_file.write(json.dumps(self.nodes_available_time))

    def log_received_hello(self, hello_packet: Hello):
        s = hello_packet.sender_port

    def log_bidirectional_neighbors(self, new_bidirectional_neighbors: list):
        self.current_bidirectional_neighbors = new_bidirectional_neighbors

    def logger_timer_task(self):
        while not self.destroy:
            time.sleep(1)
            for node_port in self.current_bidirectional_neighbors:
                self.nodes_available_time[node_port] = self.nodes_available_time.setdefault(node_port, 0) + 1
