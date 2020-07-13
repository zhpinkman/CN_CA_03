import sys
import socket
import multiprocessing
import threading
import time
import pickle
from UdpHandler import server_task, send_to


class P2PNode:
    def __init__(self, udp_ip, port, possible_neighbors_ports: list):
        print("- Process on port " + str(port) + " Started")
        self.udp_ip = udp_ip
        self.port = port
        self.possible_neighbors_ports = possible_neighbors_ports.remove(port)
        self.server_thread = None

        self.init_server()
        # print(sock.getpeername())

    def init_server(self):
        self.server_thread = threading.Thread(target=server_task, name='SERVER_TASK', args=(self.udp_ip, self.port,))
        self.server_thread.start()
