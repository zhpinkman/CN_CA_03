import sys
import socket
import multiprocessing
import threading
import time


class P2PNode:
    def __init__(self, udp_ip, port):
        print("- Process on port " + str(port) + " Started")
        sys.stdout.flush()
        self.port = port
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((udp_ip, port))
        # print(sock.getpeername())
