# 启动QCS节点
from src.ClientNode import ClientNode
from src.QCSNode import QCSNode


def start_qcs(node_id, port, other_ports):
    qcs = QCSNode(node_id, port, other_ports)
    qcs.start()


# 启动Client并发送请求数据
def start_client(data, server_ports, client_port):
    client = ClientNode(data, server_ports, client_port)
    client.start()


if __name__ == '__main__':
    # 配置QCS节点的端口
    client_port = 6000
    qcs_ports = [6001, 6002, 6003, 6004]

    # 启动QCS节点
    for i, port in enumerate(qcs_ports, 1):
        other_ports = [p for p in qcs_ports if p != port]
        start_qcs(i, port, other_ports)

    # 启动Client发送请求数据
    client_data = {"formula": "x^2 + y^2", "values": {"x": 3, "y": 4}}
    start_client(client_data, qcs_ports, client_port)
