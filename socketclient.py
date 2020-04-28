"""
两个线程，一个发一个显示，显示格式存在问题
"""
import socket

import threading
import logging

logging.basicConfig(level=logging.INFO, )
event = threading.Event()
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

addr = ('127.0.0.1', 9999)

client.connect(addr)

client.send('heelo'.encode('utf8'))


def getmessage(conn):
    while not event.isSet():
        data = conn.recv(1024).decode()
        logging.info(data + '\n>>>')


threading.Thread(target=getmessage, args=(client,), daemon=True).start()

while not event.isSet():
    ip = input('>>>')
    if ip == 'quit':
        event.set()
    client.send(ip.encode())
client.close()

# data = client.recv(1024)
