import threading
import time
from pathlib import Path
import json

from Hello import Hello
from config import UDP_PORTs, DISCONNECT_TIME_LIMIT
from graph import draw_graph

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
        self.topology_last_update_time = dict()
        self.all_neighbors = dict()
        for port1 in UDP_PORTs:
            self.topology[self.make_node_id(port1)] = dict()
            self.topology_last_update_time[self.make_node_id(port1)] = dict()
            for port2 in UDP_PORTs:
                self.topology[self.make_node_id(port1)][self.make_node_id(port2)] = False
                self.topology_last_update_time[self.make_node_id(port1)][self.make_node_id(port2)] = int(time.time())

        self.timer_thread = threading.Thread(target=self.logger_timer_task, name='LOGGER_TIMER_TASK')
        self.timer_thread.start()

    def log_received_hello(self, hello_packet: Hello):
        if hello_packet.sender_port in self.current_bidirectional_neighbors:
            sender_id = self.make_node_id(hello_packet.sender_port)
            if sender_id not in self.all_neighbors.keys():
                self.all_neighbors[sender_id] = dict()
            self.all_neighbors[sender_id]["received"] = self.all_neighbors[sender_id].setdefault("received", 0) + 1

        for port in UDP_PORTs:
            if port in hello_packet.sender_neighbors_list:
                self.topology[self.make_node_id(hello_packet.sender_port)][self.make_node_id(port)] = True
                self.topology[self.make_node_id(port)][self.make_node_id(hello_packet.sender_port)] = True
                self.topology_last_update_time[self.make_node_id(hello_packet.sender_port)][
                    self.make_node_id(port)] = int(time.time())
                self.topology_last_update_time[self.make_node_id(port)][
                    self.make_node_id(hello_packet.sender_port)] = int(time.time())
            else:
                self.topology[self.make_node_id(hello_packet.sender_port)][self.make_node_id(port)] = False
                self.topology[self.make_node_id(port)][self.make_node_id(hello_packet.sender_port)] = False

    def log_sent_hello_to_neighbor(self, neighbor_port):
        sender_id = self.make_node_id(neighbor_port)
        if sender_id not in self.all_neighbors.keys():
            self.all_neighbors[sender_id] = dict()
        self.all_neighbors[sender_id]["sent"] = self.all_neighbors[sender_id].setdefault("sent", 0) + 1

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
        self.wrap_up_1_neighbors_interaction(path)
        self.wrap_up_2_current_neighbors(path)
        self.wrap_up_3_available_time(path)
        self.wrap_up_4_topology(path)

    def wrap_up_1_neighbors_interaction(self, path):
        with open(path + "/1_neighbors_interaction.json", "w") as available_file:
            available_file.write(json.dumps(self.all_neighbors))

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
        for port1 in UDP_PORTs:
            for port2 in UDP_PORTs:
                elapsed_time = int(time.time()) - self.topology_last_update_time[self.make_node_id(port1)][
                    self.make_node_id(port2)]
                if elapsed_time >= DISCONNECT_TIME_LIMIT:
                    self.topology[self.make_node_id(port1)][self.make_node_id(port2)] = False
                    self.topology[self.make_node_id(port2)][self.make_node_id(port1)] = False

        for uni_port in self.current_unidirectional_neighbors:
            self.topology[self.make_node_id(uni_port)][self.make_node_id(self.port)] = True

        for port in UDP_PORTs:
            if port in self.current_bidirectional_neighbors:
                self.topology[self.make_node_id(port)][self.make_node_id(self.port)] = True
                self.topology[self.make_node_id(self.port)][self.make_node_id(port)] = True
            else:
                self.topology[self.make_node_id(self.port)][self.make_node_id(port)] = False

        with open(path + "/4_topology.json", "w") as available_file:
            available_file.write(json.dumps(self.topology))
        plt = draw_graph(self.topology, [self.make_node_id(port) for port in UDP_PORTs])
        plt.savefig(path + "/4_topology.png", bbox_inches='tight')

    def make_node_id(self, port):
        return str(self.ip) + ":" + str(port)
