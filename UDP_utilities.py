import sys
import socket
import multiprocessing
import threading
import time
import pickle


def server_task(udp_ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((udp_ip, port))
    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print("received message: %s" % data)
        print(pickle.loads(data))


def send_to(obj, udp_ip, udp_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(pickle.dumps(obj), (udp_ip, udp_port))
