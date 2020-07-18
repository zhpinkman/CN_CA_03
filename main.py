import multiprocessing
import time
from random import randint

from P2PNode import P2PNode
from config import RUN_DURATION, UDP_PORTs, UDP_IP


def p2p_task(udp_ip, port, node_is_running):
    p2p_node = P2PNode(udp_ip, port, UDP_PORTs, node_is_running)
    return p2p_node


def timer_task(node_is_running):
    counter = 0
    waiting_queue = []
    while counter * 10 < RUN_DURATION:
        print("Time passed: " + str(counter*10) + "s/" + str(RUN_DURATION) + "s")
        random_port = UDP_PORTs[randint(0, 5)]
        if node_is_running[random_port]:
            node_is_running[random_port] = False
            waiting_queue.append((random_port, counter + 2))
            print(str(random_port) + " Stopped!")
        if waiting_queue[0][1] <= counter:
            node_is_running[waiting_queue[0][0]] = True
            waiting_queue.pop(0)
        counter += 1
        time.sleep(10)


def main():
    print("Hi")
    node_is_running = multiprocessing.Manager().dict()
    for udp_port in UDP_PORTs:
        node_is_running[udp_port] = True

    processes_list = []
    for port in UDP_PORTs:
        process = multiprocessing.Process(target=p2p_task, args=(UDP_IP, port, node_is_running))
        process.start()
        processes_list.append(process)
    timer_process = multiprocessing.Process(target=timer_task, args=(node_is_running,))
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
