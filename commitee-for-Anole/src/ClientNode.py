import json
import socket
import threading
from collections import Counter


class ClientNode:
    def __init__(self, data, server_ports, client_port):
        self.data = data
        self.server_ports = server_ports
        self.client_port = client_port
        self.vote = []
        self.vote_count = Counter()

    def start(self):
        """启动Client，发送数据到QCS节点"""
        print(f'Client sending data: {self.data}')
        threading.Thread(target=self.listen_for_result, daemon=True).start()
        for port in self.server_ports:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', port))
                message = {
                    'type': '0',
                    'data': self.data
                }
                s.sendall(json.dumps(message).encode())

    def listen_for_result(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', self.client_port))
            s.listen(5)
            print(f'Client listening on port {self.client_port}')
            while True:
                conn, addr = s.accept()
                with conn:
                    result = json.loads(conn.recv(1024).decode())
                    self.vote.append(result)
                    self.vote_count[str(result)] += 1
                    if len(self.vote) == self.vote_count.most_common(1)[0][1] == 4:
                        print(f'Client received vote: {self.vote_count.most_common(1)[0][1]}')
