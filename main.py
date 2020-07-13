import sys
import socket
import multiprocessing
import threading
import time

UDP_IP = "localhost"
UDP_PORTs = [9001, 9002, 9003, 9004, 9005, 9006]




def p2p_task(port):
    p2p_node = P2PNode(port)


def main():
    print("Hi")
    processes_list = []
    for port in UDP_PORTs:
        process = multiprocessing.Process(target=p2p_task, args=(port,))
        process.run()
        process.start()
        processes_list.append(process)

    while True:
        command = input("* enter exit to quit\n")
        print("Killing processes")
        if command == "exit":
            for process in processes_list:
                process.kill()
            break


if __name__ == '__main__':
    main()
