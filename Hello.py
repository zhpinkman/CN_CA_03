class Hello:
    def __init__(self, sender_id, sender_ip, sender_port, packet_type, sender_neighbors_list, sender_last_send_time,
                 sender_last_receive_time):
        self.sender_id = sender_id
        self.sender_ip = sender_ip
        self.sender_port = sender_port
        self.packet_type = packet_type
        self.sender_neighbors_list = sender_neighbors_list
        self.sender_last_send_time = sender_last_send_time
        self.sender_last_receive_time = sender_last_receive_time

    