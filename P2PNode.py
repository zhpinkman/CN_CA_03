import sys
import socket
import multiprocessing
import threading
import time
import pickle
import time
from UDP_utilities import send_to
from Hello import Hello


class P2PNode:
    def __init__(self, udp_ip, port, possible_neighbors_ports: []):
        print("- Process on port " + str(port) + " Started")
        self.udp_ip = udp_ip
        self.port = port
        self.possible_neighbors_ports = possible_neighbors_ports.remove(port)
        self.server_thread = None
        self.bidirectional_neighbors = []
        self.last_receive_time = dict()

        self.init_server()
        self.init_timer_functions()
        # print(sock.getpeername())

    def init_server(self):
        self.server_thread = threading.Thread(target=self.server_task, name='SERVER_TASK',
                                              args=(self.udp_ip, self.port,))
        self.server_thread.start()

    def server_task(self, udp_ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((udp_ip, port))
        while True:
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            print(str(self.port) + " received message: ------------------------")
            hello_packet: Hello = pickle.loads(data)
            print(hello_packet.sender_last_send_time)

    def init_timer_functions(self):
        self.server_thread = threading.Thread(target=self.timer_task, name='TIMER_TASK')
        self.server_thread.start()

    def timer_task(self):  # runs every second
        while True:
            # print("Sent something")
            epoch_time = int(time.time())
            hello_packet = Hello(self.port, self.udp_ip, self.port, "udp", self.bidirectional_neighbors, epoch_time, 0)
            send_to(hello_packet, self.udp_ip, 9001)
            time.sleep(1)
