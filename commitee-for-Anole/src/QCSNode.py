import json
import threading
import socket
from collections import Counter

NUM_QCS = 4


class QCSNode:
    def __init__(self, node_id, port, other_ports):
        self.node_id = node_id
        self.port = port
        self.other_ports = other_ports
        self.data = None
        self.received_data = []
        self.data_count = Counter()

    def start(self):
        threading.Thread(target=self.listen_for_messages).start()

    def listen_for_messages(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', self.port))
            s.listen()
            print(f'QCS Node {self.node_id} listening on port: {self.port}')
            while True:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(1024)
                    if data:
                        message = json.loads(data.decode())
                        self.handle_message(message)

    def handle_message(self, message):
        if message['type'] == '0':
            # DO ENCODE
            # BLS 签名操作
            message['type'] = '1'
            self.received_data.append(message)
            self.data_count[str(message['data'])] += 1
            self.propagate_data(message)
        elif message['type'] == '1':
            # BLS 验签操作
            self.received_data.append(message)
            self.data_count[str(message['data'])] += 1
            print(f'QCS {self.node_id} received message')
            # print(f'QCS {self.node_id} received {len(self.received_data)} data')
            # print(message)
            print(f'Statistics: {self.data_count}')
            if len(self.received_data) < NUM_QCS:
                print("Need more data")
            else:
                if self.data_count.most_common(1)[0][1] >= NUM_QCS - 1:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect(('localhost', 6000))
                        s.sendall(json.dumps(1).encode())
                else:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect(('localhost', 6000))
                        s.sendall(json.dumps(0).encode())
                print(f'QCS {self.node_id} stopped')

    def propagate_data(self, data):
        """ 将数据传播给其他 QCS 节点 """
        for port in self.other_ports:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', port))
                message = data
                s.sendall(json.dumps(message).encode())
