import pickle
import socket


def send_to(obj, udp_ip, udp_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(pickle.dumps(obj), (udp_ip, udp_port))
    sock.close()
