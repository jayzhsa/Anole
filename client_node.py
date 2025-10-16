# -*- coding: utf-8 -*-
import json
import socket
import time
import logging
import sys
import threading
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('client_node.log')
    ]
)

class ClientNode:
    def __init__(self, qcs_nodes, port=9000):
        self.qcs_nodes = qcs_nodes  # List of (ip, port) tuples
        self.port = port
        self.votes = []
        self.start_time = time.time()

    def send_data(self, data):
        # message = { #Join/Leave
        #     'type': '0',
        #     'data': data
        # }
        message = { #Complain
            'type': '2',
            'complain_node': random.randint(1, 2)
        }
        # message = { #证书处理
        #     'type': '4',
        #     'data': 'CERTIFICATE'
        # }
        for ip, port in self.qcs_nodes:
            for _ in range(5):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect((ip, port))
                        s.sendall(json.dumps(message).encode())
                        logging.info("[Client] 成功发送数据到 {}:{}".format(ip, port))
                        break
                except Exception as e:
                    logging.info("[Client] 连接 {}:{} 失败，重试... {}".format(ip, port, e))
                    time.sleep(0.1)
        logging.info("[Client] 发送数据: {}".format(data))

    def receive_votes(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', self.port))
                s.listen(20)
                s.settimeout(30)  # 30秒超时
                logging.info("[Client] 监听端口: {}".format(self.port))
                while len(self.votes) < 3:
                    try:
                        conn, addr = s.accept()
                        with conn:
                            data = conn.recv(100000)
                            if data:
                                try:
                                    vote = json.loads(data.decode())
                                    self.votes.append(vote)
                                    logging.info("[Client] 收到投票结果: {} 从 {}".format(vote, addr))
                                except Exception as e:
                                    logging.error("[Client] 解析投票结果失败: {}".format(e))
                    except socket.timeout:
                        logging.warning("[Client] 接收投票超时，当前收到 {} 条投票".format(len(self.votes)))
                        break
                    except Exception as e:
                        logging.error("[Client] 接收投票错误: {}".format(e))
        except Exception as e:
            logging.error("[Client] 监听端口失败: {}".format(e))
        return self.votes

    def start(self):
        data = "h"
        self.send_data(data)
        votes = self.receive_votes()
        end_time = time.time()
        logging.info("[Client] 耗时: {:.4f}秒".format(end_time - self.start_time))
        return votes

if __name__ == "__main__":
    qcs_nodes = [
        ("115.29.176.22", 5000),  # kkk1
        ("47.111.121.121", 5001),  # kkk2
        ("47.111.111.4", 5002)     # kkk3
    ]
    client = ClientNode(qcs_nodes, port=9000)
    votes = client.start()
    logging.info("[Client] 最终投票结果: {}".format(votes))