import sys
import socket
import multiprocessing
import threading
import time
import pickle


def send_to(obj, udp_ip, udp_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(pickle.dumps(obj), (udp_ip, udp_port))
