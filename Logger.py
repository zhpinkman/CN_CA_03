import threading
import time
from pathlib import Path
import json

from Hello import Hello
from config import UDP_PORTs

RESULT_FOLDER = "RESULTS"


class Logger:
    def __init__(self, ip, port):
        self.current_unidirectional_neighbors = []
        self.ip = ip
        self.port = port
        self.current_bidirectional_neighbors = []
        self.nodes_available_time = dict()
        self.destroy = False
        self.topology = dict()
        for port1 in UDP_PORTs:
            self.topology[self.make_node_id(port1)] = dict()
            for port2 in UDP_PORTs:
                self.topology[self.make_node_id(port1)][self.make_node_id(port2)] = False

        self.timer_thread = threading.Thread(target=self.logger_timer_task, name='LOGGER_TIMER_TASK')
        self.timer_thread.start()

    def log_received_hello(self, hello_packet: Hello):
        for port in UDP_PORTs:
            if port in hello_packet.sender_neighbors_list:
                self.topology[self.make_node_id(hello_packet.sender_port)][self.make_node_id(port)] = True
                self.topology[self.make_node_id(port)][self.make_node_id(hello_packet.sender_port)] = True
            else:
                self.topology[self.make_node_id(hello_packet.sender_port)][self.make_node_id(port)] = False
                self.topology[self.make_node_id(port)][self.make_node_id(hello_packet.sender_port)] = False

    def log_bidirectional_neighbors(self, new_bidirectional_neighbors: list):
        self.current_bidirectional_neighbors = new_bidirectional_neighbors

    def log_unidirectional_neighbors(self, new_unidirectional_neighbors: list):
        self.current_unidirectional_neighbors = new_unidirectional_neighbors

    def logger_timer_task(self):
        while not self.destroy:
            time.sleep(1)
            for node_port in self.current_bidirectional_neighbors:
                node_id = self.make_node_id(node_port)
                self.nodes_available_time[node_id] = self.nodes_available_time.setdefault(node_id, 0) + 1

    def terminate(self, overall_time_in_seconds):
        self.destroy = True
        self.wrap_up(overall_time_in_seconds)

    def wrap_up(self, overall_time_in_seconds):
        path = RESULT_FOLDER + "/" + str(self.ip) + "_" + str(self.port)
        Path(path).mkdir(parents=True, exist_ok=True)
        self.wrap_up_2_current_neighbors(path)
        self.wrap_up_3_available_time(path)
        self.wrap_up_4_topology(path)
        
    def wrap_up_2_current_neighbors(self, path):
        ip_port_list = []
        for port in self.current_bidirectional_neighbors:
            ip_port_list.append(self.make_node_id(port))
        with open(path + "/2_last_bidirectional_neighbors.json", "w") as available_file:
            available_file.write(json.dumps(ip_port_list))

    def wrap_up_3_available_time(self, path):
        with open(path + "/3_available_time_in_seconds.json", "w") as available_file:
            available_file.write(json.dumps(self.nodes_available_time))

    def wrap_up_4_topology(self, path):
        for uni_port in self.current_unidirectional_neighbors:
            self.topology[self.make_node_id(uni_port)][self.make_node_id(self.port)] = True
        for bi_port in self.current_bidirectional_neighbors:
            self.topology[self.make_node_id(bi_port)][self.make_node_id(self.port)] = True
            self.topology[self.make_node_id(self.port)][self.make_node_id(bi_port)] = True
        with open(path + "/4_topology.json", "w") as available_file:
            available_file.write(json.dumps(self.topology))

    def make_node_id(self, port):
        return str(self.ip) + ":" + str(port)
