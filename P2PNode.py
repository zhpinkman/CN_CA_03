import pickle
import socket
import threading
import time
from random import randint

from Hello import Hello
from UDP_utilities import send_to
from Logger import Logger
from config import MAX_NEIGHBORS, DISCONNECT_TIME_LIMIT, PACKET_LOSS_PROB_THRESHOLD, RUN_DURATION


class P2PNode:
    def __init__(self, udp_ip, port, possible_neighbors_ports: [], node_is_running):
        print("- Process on port " + str(port) + " Started")
        self.node_is_running = node_is_running
        self.udp_ip = udp_ip
        self.port = port
        self.possible_neighbors_ports: list = possible_neighbors_ports
        self.possible_neighbors_ports.remove(port)
        self.bidirectional_neighbors = []  # real neighbors
        self.unidirectional_neighbors = []  # those who want to be neighbors with us
        self.temporary_neighbors = []  # those we want to be neighbors with them
        self.node_logger = Logger(self.udp_ip, self.port)
        self.destroy = False
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

    def move_host_to(self, host_port, to_move_list: list):
        try:
            self.bidirectional_neighbors.remove(host_port)
        except ValueError:
            pass
        try:
            self.unidirectional_neighbors.remove(host_port)
        except ValueError:
            pass
        try:
            self.temporary_neighbors.remove(host_port)
        except ValueError:
            pass
        to_move_list.append(host_port)
        if to_move_list == self.bidirectional_neighbors:
            self.node_logger.log_bidirectional_neighbors(self.bidirectional_neighbors)

    def server_task(self, udp_ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((udp_ip, port))
        while not self.destroy:
            if self.node_is_running[self.port]:
                data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
                # ignore packets with probability of less than 5 in 100
                if randint(0, 100) > PACKET_LOSS_PROB_THRESHOLD:
                    continue
                received_hello_packet: Hello = pickle.loads(data)
                self.node_logger.log_received_hello(received_hello_packet)
                sender_port = received_hello_packet.sender_port
                self.last_receive_time[sender_port] = int(time.time())

                if len(
                        self.bidirectional_neighbors) < MAX_NEIGHBORS and sender_port not in self.bidirectional_neighbors:
                    if sender_port in self.temporary_neighbors or self.port in received_hello_packet.sender_neighbors_list:
                        self.move_host_to(sender_port, self.bidirectional_neighbors)
                        self.print_neighbors()
                    else:
                        self.move_host_to(sender_port, self.unidirectional_neighbors)

                # print(str(self.port) + " received message: ", end="")
                # print(received_hello_packet.sender_neighbors_list)
            else:
                pass

    def init_timer_functions(self):
        threading.Thread(target=self.send_hello_timer_task, name='TIMER_TASK1').start()
        threading.Thread(target=self.delete_neighbor_timer_task, name='TIMER_TASK2').start()
        threading.Thread(target=self.search_for_new_neighbors_timer_task, name='TIMER_TASK3').start()
        threading.Thread(target=self.destruction_timer_task(), name='TIMER_TASK4').start()

    def destruction_timer_task(self):
        time.sleep(RUN_DURATION)
        print("node " + str(self.udp_ip) + ":" + str(self.port) + " destroyed!")
        self.node_logger.terminate(RUN_DURATION)
        self.destroy = True

    def send_hello_timer_task(self):  # runs every second
        while not self.destroy:
            if self.node_is_running[self.port]:
                for neighbor_port in self.bidirectional_neighbors:
                    hello_packet = self.make_hello_packet(neighbor_port)
                    send_to(hello_packet, self.udp_ip, neighbor_port)
                if len(self.bidirectional_neighbors) < MAX_NEIGHBORS:
                    for host_port in set().union(self.unidirectional_neighbors, self.temporary_neighbors):
                        hello_packet = self.make_hello_packet(host_port)
                        send_to(hello_packet, self.udp_ip, host_port)
                time.sleep(2)

    def delete_neighbor_timer_task(self):
        while not self.destroy:
            if self.node_is_running[self.port]:
                for neighbor_port in self.bidirectional_neighbors:
                    if int(time.time()) - self.last_receive_time[neighbor_port] >= DISCONNECT_TIME_LIMIT:
                        self.bidirectional_neighbors.remove(neighbor_port)
                        self.node_logger.log_bidirectional_neighbors(self.bidirectional_neighbors)
                        self.print_neighbors()
                for neighbor_port in self.unidirectional_neighbors:
                    if int(time.time()) - self.last_receive_time[neighbor_port] >= DISCONNECT_TIME_LIMIT:
                        self.unidirectional_neighbors.remove(neighbor_port)
                time.sleep(1)

    def search_for_new_neighbors_timer_task(self):
        search_start_time = 0
        while not self.destroy:
            if self.node_is_running[self.port]:
                if int(time.time()) - search_start_time >= DISCONNECT_TIME_LIMIT:
                    self.temporary_neighbors.clear()
                if len(self.bidirectional_neighbors) < MAX_NEIGHBORS and len(self.temporary_neighbors) == 0:
                    neighbor_port = self.possible_neighbors_ports[randint(0, len(self.possible_neighbors_ports) - 1)]
                    self.temporary_neighbors.append(neighbor_port)
                    search_start_time = int(time.time())
                    # send_to(self.make_hello_packet(neighbor_port), self.udp_ip, neighbor_port)
                    # send_hello_timer_task will do it

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

    def print_neighbors(self):
        print(str(self.port), end=": ")
        print(self.bidirectional_neighbors)
