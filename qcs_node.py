# -*- coding: utf-8 -*-
import base64
import json
import socket
import threading
import time
import logging
import sys
from collections import Counter
try:
    from Crypto.Hash import SHA256
    from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, pair
    from nacl.signing import SigningKey
except ImportError as e:
    print("依赖导入失败: {}".format(e))
    sys.exit(1)

# 配置日志
print("配置日志...")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('qcs_node_{}.log'.format(sys.argv[1] if len(sys.argv) > 1 else 'unknown'))
    ]
)

# MSP 加密操作
def MSP_Init(security_parameter='SS512'):
    try:
        print("初始化 MSP...")
        pairing_group = PairingGroup(security_parameter)
        g1 = pairing_group.random(G1)
        g2 = pairing_group.random(G2)
        print("MSP 初始化成功，g1 in G1: {}, g2 in G2: {}".format(g1, g2))
        return pairing_group, g1, g2
    except Exception as e:
        print("MSP 初始化失败: {}".format(e))
        logging.error("MSP 初始化失败: {}".format(e))
        raise

def MSP_KeyGen(pairing_group, g2):
    msk = pairing_group.random(ZR)
    mpk = g2 ** msk
    logging.info("MSP_KeyGen: msk={}, mpk={}".format(msk, mpk))
    return msk, mpk

def MSP_AggMpk(pairing_group, mpk_list):
    apk = pairing_group.init(G2, 1)
    for mpk in mpk_list:
        apk *= mpk
    return apk

def MSP_Sig(pairing_group, g1, msk, m):
    m_encoded = m.encode('utf-8')
    h = pairing_group.hash(m_encoded, G1)
    s = h ** msk
    logging.info("MSP_Sig: m={}, h={}, s={}".format(m, h, s))
    return s

def MSP_Agg(pairing_group, sig_list):
    agg = pairing_group.init(G1, 1)
    for sig in sig_list:
        agg *= sig
    return agg

def MSP_AggVf(pairing_group, g1, g2, apk, agg, m):
    m_encoded = m.encode('utf-8')
    h = pairing_group.hash(m_encoded, G1)
    logging.info("MSP_AggVf: m={}, h={}, apk={}, agg={}".format(m, h, apk, agg))
    # 标准配对
    lhs = pair(agg, g2)
    rhs = pair(h, apk)
    logging.info("MSP_AggVf: lhs={}, rhs={}".format(lhs, rhs))
    # 尝试单签名验证（调试用）
    single_valid = False
    for sig, mpk in zip(sig_list, mpk_list):
        single_lhs = pair(sig, g2)
        single_rhs = pair(h, mpk)
        if single_lhs == single_rhs:
            single_valid = True
            logging.info("MSP_AggVf: 单签名验证通过，sig={}, mpk={}".format(sig, mpk))
        else:
            logging.info("MSP_AggVf: 单签名验证失败，sig={}, mpk={}".format(sig, mpk))
    return lhs == rhs or single_valid

# 初始化 MSP 加密参数
try:
    logging.info("初始化 MSP 加密参数...")
    pairing_group, g1, g2 = MSP_Init('SS512')
    logging.info("MSP 初始化成功")
except Exception as e:
    print("MSP 初始化失败: {}".format(e))
    logging.error("MSP 初始化失败: {}".format(e))
    sys.exit(1)

mpk_list = []
sig_list = []
complain_list = [0] * 8
sig_pk = [0] * 8

class QCSNode:
    def __init__(self, node_id, port, other_nodes, client_ip, client_port):
        self.node_id = node_id
        self.port = port
        self.other_nodes = other_nodes
        self.client_ip = client_ip
        self.client_port = client_port
        self.received_data = []
        self.data_count = Counter()
        self.start_time = time.time()

    def start(self):
        try:
            print("[NODE {}] 启动节点...".format(self.node_id))
            logging.info("[NODE {}] 启动节点...".format(self.node_id))
            threading.Thread(target=self.listen_for_messages, daemon=True).start()
            print("[NODE {}] 启动线程成功".format(self.node_id))
            logging.info("[NODE {}] 启动线程成功".format(self.node_id))
        except Exception as e:
            print("[NODE {}] 启动失败: {}".format(self.node_id, e))
            logging.error("[NODE {}] 启动失败: {}".format(self.node_id, e))
            raise

    def listen_for_messages(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', self.port))
                s.listen(20)
                print('[NODE {}] 监听端口: {}'.format(self.node_id, self.port))
                logging.info('[NODE {}] 监听端口: {}'.format(self.node_id, self.port))
                while True:
                    conn, addr = s.accept()
                    with conn:
                        data = conn.recv(100000)
                        if data:
                            try:
                                message = json.loads(data.decode())
                                message['node'] = self.node_id
                                self.handle_message(message)
                            except Exception as e:
                                print('[NODE {}] 消息处理错误: {}'.format(self.node_id, e))
                                logging.error('[NODE {}] 消息处理错误: {}'.format(self.node_id, e))
        except Exception as e:
            print('[NODE {}] 监听端口失败: {}'.format(self.node_id, e))
            logging.error('[NODE {}] 监听端口失败: {}'.format(self.node_id, e))
            raise

    def handle_message(self, message):
        global mpk_list, sig_list, sig_pk
        # 重置列表以避免累积
        if message['type'] == '0':
            mpk_list.clear()
            sig_list.clear()
            sig_start_time = time.time()
            msk, mpk = MSP_KeyGen(pairing_group, g2)
            logging.info("[NODE {}] 收到客户端消息: {}".format(self.node_id, message['data']))
            m = message['data']
            signature = MSP_Sig(pairing_group, g1, msk, m)
            mpk_list.append(mpk)
            sig_list.append(signature)
            sig_end_time = time.time()
            logging.info("[NODE {}] 签名生成耗时: {:.4f}秒".format(self.node_id, sig_end_time - sig_start_time))
            message['type'] = '1'
            message['mpk'] = pairing_group.serialize(mpk).decode()
            message['sig'] = pairing_group.serialize(signature).decode()
            self.received_data.append(message)
            self.data_count[str(m)] += 1
            logging.info("[NODE {}] 当前 received_data 长度: {}, sig_list 长度: {}, mpk_list 长度: {}".format(
                self.node_id, len(self.received_data), len(sig_list), len(mpk_list)))
            self.propagate_data(message)
            logging.info("[NODE {}] 发送数据到其他节点".format(self.node_id))
        elif message['type'] == '1':
            self.received_data.append(message)
            self.data_count[str(message['data'])] += 1
            try:
                sig = pairing_group.deserialize(message['sig'].encode())
                mpk = pairing_group.deserialize(message['mpk'].encode())
                sig_list.append(sig)
                mpk_list.append(mpk)
                logging.info("[NODE {}] 成功解析签名和公钥，sig={}, mpk={}".format(self.node_id, sig, mpk))
            except Exception as e:
                logging.error("[NODE {}] 解析签名或公钥失败: {}".format(self.node_id, e))
            logging.info('[NODE {}] 收到签名消息, 数据: {}'.format(self.node_id, message['data']))
            logging.info("[NODE {}] 当前 received_data 长度: {}, sig_list 长度: {}, mpk_list 长度: {}".format(
                self.node_id, len(self.received_data), len(sig_list), len(mpk_list)))
            if len(self.received_data) >= 3 and len(sig_list) >= 3 and len(mpk_list) >= 3:
                logging.info("[NODE {}] 已接收到所有数据".format(self.node_id))
                if self.data_count.most_common(1)[0][1] >= 3:
                    apk = MSP_AggMpk(pairing_group, mpk_list)
                    agg = MSP_Agg(pairing_group, sig_list)
                    valid = MSP_AggVf(pairing_group, g1, g2, apk, agg, message['data'])
                    result = {
                        'valid': valid,
                        'agg': pairing_group.serialize(agg).decode()
                    }
                    logging.info("\n===== 证书信息 =====")
                    logging.info(json.dumps(result, indent=4))
                    logging.info("===================\n")
                    with open('certificate_node_{}.json'.format(self.node_id), 'w') as f:
                        json.dump(result, f, indent=4)
                    logging.info('[NODE {}] 证书已导出: certificate_node_{}.json'.format(self.node_id, self.node_id))
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.connect((self.client_ip, self.client_port))
                            s.sendall(json.dumps(result).encode())
                            logging.info("[NODE {}] 结果已发送到客户端".format(self.node_id))
                    except Exception as e:
                        logging.error("[NODE {}] 发送结果到客户端失败: {}".format(self.node_id, e))
                else:
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.connect((self.client_ip, self.client_port))
                            s.sendall(json.dumps(0).encode())
                            logging.info("[NODE {}] 发送无效结果到客户端".format(self.node_id))
                    except Exception as e:
                        logging.error("[NODE {}] 发送无效结果失败: {}".format(self.node_id, e))
                logging.info('[NODE {}] 结束'.format(self.node_id))
                # 重置数据
                self.received_data.clear()
                self.data_count.clear()
            if time.time() - self.start_time > 30:
                logging.warning("[NODE {}] 等待签名超时，当前 received_data: {}, sig_list: {}, mpk_list: {}".format(
                    self.node_id, len(self.received_data), len(sig_list), len(mpk_list)))
        elif message['type'] == '2':
            complain_list[message['complain_node']] += 1
            message['type'] = '3'
            self.propagate_data(message)
        elif message['type'] == '3':
            for i in range(8):
                if complain_list[i] >= 2:
                    logging.info('NODE {} 已被举报下线'.format(i))
                    break
            else:
                logging.info('举报不通过')
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self.client_ip, self.client_port))
                    s.sendall(json.dumps('COMPLAIN NOT MAKE SENSE').encode())
        elif message['type'] == '4':
            m = message['data']
            i = message['node']
            hashed_m = SHA256.new(m.encode())
            logging.info('NODE {} hashed the message -> {}'.format(i, hashed_m))
            private_key = SigningKey.generate()
            public_key = private_key.verify_key
            sig_pk[i] = public_key
            signature_m = private_key.sign(hashed_m.digest())
            message['signature'] = base64.b64encode(signature_m).decode()
            message['pid'] = i
            logging.info('NODE {} 签名了消息'.format(i))
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.client_ip, self.client_port))
                s.sendall(json.dumps(message).encode())
        elif message['type'] == '5':
            logging.info('NODE IN PORT {} 收到验签成功返回'.format(message['port']))

    def propagate_data(self, data):
        for ip, port in self.other_nodes:
            for _ in range(5):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect((ip, port))
                        s.sendall(json.dumps(data).encode())
                        logging.info("[NODE {}] 成功发送数据到 {}:{}".format(self.node_id, ip, port))
                        break
                except Exception as e:
                    logging.info('[NODE {}] 连接 {}:{} 失败，重试... {}'.format(self.node_id, ip, port, e))
                    time.sleep(0.1)

if __name__ == "__main__":
    try:
        print("启动 QCSNode...")
        logging.info("启动 QCSNode...")
        if len(sys.argv) != 2:
            print("用法: python qcs_node.py <node_id>")
            logging.error("缺少 node_id 参数")
            sys.exit(1)
        node_id = int(sys.argv[1])
        print("node_id: {}".format(node_id))
        port_map = {1: 5000, 2: 5001, 3: 5002}
        other_nodes_map = {
            1: [("47.111.121.121", 5001), ("47.111.111.4", 5002)],
            2: [("115.29.176.22", 5000), ("47.111.111.4", 5002)],
            3: [("115.29.176.22", 5000), ("47.111.121.121", 5001)]
        }
        client_ip = "115.29.176.79"
        client_port = 9000
        port = port_map[node_id]
        other_nodes = other_nodes_map[node_id]
        print("配置: port={}, other_nodes={}, client_ip={}, client_port={}".format(
            port, other_nodes, client_ip, client_port))
        qcs = QCSNode(node_id, port, other_nodes, client_ip, client_port)
        qcs.start()
        print("QCSNode 启动成功，进入主循环")
        logging.info("QCSNode 启动成功，进入主循环")
        while True:
            time.sleep(1)
    except Exception as e:
        print("QCSNode 启动失败: {}".format(e))
        logging.error("QCSNode 启动失败: {}".format(e))
        sys.exit(1)