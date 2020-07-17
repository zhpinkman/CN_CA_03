import multiprocessing
import time
from random import randint

from P2PNode import P2PNode

UDP_IP = "localhost"
UDP_PORTs = [9001, 9002, 9003, 9004, 9005, 9006]  # NODES = 6
manager = multiprocessing.Manager()
node_is_running = manager.dict()
for udp_port in UDP_PORTs:
    node_is_running[udp_port] = True


def p2p_task(udp_ip, port):
    p2p_node = P2PNode(udp_ip, port, UDP_PORTs, node_is_running)
    return p2p_node


def timer_task():
    counter = 0
    waiting_queue = []
    while True:
        random_port = UDP_PORTs[randint(0, 5)]
        if node_is_running[random_port]:
            node_is_running[random_port] = False
            waiting_queue.append((random_port, counter + 2))
        if waiting_queue[0][1] == counter:
            node_is_running[waiting_queue[0][0]] = True
            waiting_queue.pop(0)
        counter += 1
        time.sleep(10)


def main():
    print("Hi")
    processes_list = []
    for port in UDP_PORTs:
        process = multiprocessing.Process(target=p2p_task, args=(UDP_IP, port,))
        process.start()
        processes_list.append(process)
    timer_process = multiprocessing.Process(target=timer_task)
    timer_process.start()
    processes_list.append(timer_process)

    while True:
        command = input("* enter exit to quit\n")
        if command == "exit":
            print("Killing processes")
            for process in processes_list:
                process.kill()
            break


if __name__ == '__main__':
    main()
