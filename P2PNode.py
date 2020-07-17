import sys
import socket
import multiprocessing
import threading
import time
import pickle
import time
from random import randint
from UDP_utilities import send_to
from Hello import Hello

MAX_NEIGHBORS = 3
DISCONNECT_TIME_LIMIT = 8
PROB_THRESHOLD = 94


class P2PNode:
    def __init__(self, udp_ip, port, possible_neighbors_ports: []):
        print("- Process on port " + str(port) + " Started")
        self.udp_ip = udp_ip
        self.port = port
        self.possible_neighbors_ports: list = possible_neighbors_ports
        self.possible_neighbors_ports.remove(port)
        self.server_thread = None
        self.bidirectional_neighbors = []
        self.unidirectional_neighbors = []
        self.temporarily_neighbors = []
        self.last_receive_time = dict()
        for port in self.possible_neighbors_ports:
            self.last_receive_time[port] = -1
        self.pending_neighbor = None  # waiting for it's reply

        self.init_server()
        self.init_timer_functions()

    def init_server(self):
        self.server_thread = threading.Thread(target=self.server_task, name='SERVER_TASK',
                                              args=(self.udp_ip, self.port,))
        self.server_thread.start()

    def server_task(self, udp_ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((udp_ip, port))
        while True:
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            # ignore the packet with probablity of 5 in 100
            if randint(0, 100) > PROB_THRESHOLD:
                continue
            received_hello_packet: Hello = pickle.loads(data)
            self.last_receive_time[received_hello_packet.sender_id] = int(time.time())
            print(str(self.port) + " received message: ", end="")
            print(received_hello_packet.sender_neighbors_list)

    def init_timer_functions(self):
        threading.Thread(target=self.send_hello_timer_task, name='TIMER_TASK1').start()
        threading.Thread(target=self.delete_neighbor_timer_task, name='TIMER_TASK2').start()
        threading.Thread(target=self.search_for_new_neighbors_timer_task, name='TIMER_TASK3').start()

    def send_hello_timer_task(self):  # runs every second
        while True:
            for neighbor_port in self.bidirectional_neighbors:
                hello_packet = self.make_hello_packet(neighbor_port)
                send_to(hello_packet, self.udp_ip, neighbor_port)
            if self.pending_neighbor is not None:
                send_to(self.make_hello_packet(self.pending_neighbor), self.udp_ip, self.pending_neighbor)
            time.sleep(2)

    def delete_neighbor_timer_task(self):
        for neighbor_port in self.bidirectional_neighbors:
            if int(time.time()) - self.last_receive_time[neighbor_port] >= DISCONNECT_TIME_LIMIT:
                self.bidirectional_neighbors.remove(neighbor_port)
        time.sleep(1)

    def search_for_new_neighbors_timer_task(self):
        search_start_time = 0
        while True:
            if len()
            # if len(self.bidirectional_neighbors) < MAX_NEIGHBORS:
            #     random_port = self.possible_neighbors_ports[randint(0, len(self.possible_neighbors_ports) - 1)]
            #     while random_port in self.bidirectional_neighbors:
            #         random_port = self.possible_neighbors_ports[randint(0, len(self.possible_neighbors_ports) - 1)]

            #     self.pending_neighbor = random_port
            #     search_start_time = int(time.time())
            #     while int(time.time()) - search_start_time < DISCONNECT_TIME_LIMIT:
            #         if self.last_receive_time[random_port] >= search_start_time:
            #             self.bidirectional_neighbors.append(random_port)
            #             break
            time.sleep(1)

    def make_hello_packet(self, dest_port):
        epoch_time = int(time.time())
        return Hello(str(self.udp_ip) + ":" + str(self.port),
                     self.udp_ip,
                     self.port,
                     "udp",
                     self.bidirectional_neighbors,
                     epoch_time,
                     self.last_receive_time[dest_port])
