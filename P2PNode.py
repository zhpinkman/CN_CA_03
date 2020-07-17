import pickle
import socket
import threading
import time
from random import randint

from Hello import Hello
from UDP_utilities import send_to
from Logger import Logger

MAX_NEIGHBORS = 3
DISCONNECT_TIME_LIMIT = 8
PACKET_LOSS_PROB_THRESHOLD = 94


class P2PNode:
    def __init__(self, udp_ip, port, possible_neighbors_ports: [], node_is_running):
        print("- Process on port " + str(port) + " Started")
        self.node_is_running = node_is_running
        self.udp_ip = udp_ip
        self.port = port
        self.possible_neighbors_ports: list = possible_neighbors_ports
        self.possible_neighbors_ports.remove(port)
        self.bidirectional_neighbors = []  # those we want to be neighbors with them
        self.unidirectional_neighbors = []  # those who want to be neighbors with us
        self.temporary_neighbors = []
        self.node_logger = Logger(self.udp_ip, self.port)
        self.last_receive_time = dict()
        for port in self.possible_neighbors_ports:
            self.last_receive_time[port] = -1

        self.server_thread = self.init_server()
        self.init_timer_functions()

    def init_server(self):
        server_thread = threading.Thread(target=self.server_task, name='SERVER_TASK',
                                         args=(self.udp_ip, self.port,))
        server_thread.start()
        return server_thread

    def server_task(self, udp_ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((udp_ip, port))
        while True:
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            # ignore packets with probability of less than 5 in 100
            if randint(0, 100) > PACKET_LOSS_PROB_THRESHOLD:
                continue
            received_hello_packet: Hello = pickle.loads(data)
            sender_port = received_hello_packet.sender_port
            self.last_receive_time[sender_port] = int(time.time())
            if sender_port not in self.bidirectional_neighbors:
                if sender_port in self.temporary_neighbors and len(self.bidirectional_neighbors) < MAX_NEIGHBORS:
                    self.bidirectional_neighbors.append(sender_port)
                    self.temporary_neighbors.remove(sender_port)
                if sender_port not in self.unidirectional_neighbors:
                    self.unidirectional_neighbors.append(sender_port)
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
            if len(self.bidirectional_neighbors) < MAX_NEIGHBORS:
                for host_port in self.unidirectional_neighbors:
                    hello_packet = self.make_hello_packet(host_port)
                    send_to(hello_packet, self.udp_ip, host_port)
            time.sleep(2)

    def delete_neighbor_timer_task(self):
        while True:
            for neighbor_port in self.bidirectional_neighbors:
                if int(time.time()) - self.last_receive_time[neighbor_port] >= DISCONNECT_TIME_LIMIT:
                    self.bidirectional_neighbors.remove(neighbor_port)
            time.sleep(1)

    def search_for_new_neighbors_timer_task(self):
        search_start_time = 0
        while True:
            if len(self.bidirectional_neighbors) < MAX_NEIGHBORS:
                if len(self.unidirectional_neighbors) > 0:
                    send_to(self.make_hello_packet(self.unidirectional_neighbors[0]), self.udp_ip,
                            self.unidirectional_neighbors[0])
                    # send hello packet to the first host that sends us its hello packet
                else:
                    neighbor_port = self.possible_neighbors_ports[randint(0, len(self.possible_neighbors_ports) - 1)]
                    if neighbor_port not in self.temporary_neighbors:
                        self.temporary_neighbors.append(neighbor_port)
                    send_to(self.make_hello_packet(neighbor_port), self.udp_ip, neighbor_port)
            time.sleep(1)

    # night push akhe ? :joy
    def make_hello_packet(self, dest_port):
        epoch_time = int(time.time())
        return Hello(str(self.udp_ip) + ":" + str(self.port),
                     self.udp_ip,
                     self.port,
                     "udp",
                     self.bidirectional_neighbors,
                     epoch_time,
                     self.last_receive_time[dest_port])
