"""
server
在线人数为0时候 server端关闭
"""
import logging
import socket
import threading
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(threadName)s %(message)s")


class Server:
    def __init__(self, ip, port):
        self.event = threading.Event()
        self.cients = {}
        self.addr = ip, port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(self.addr)
        self.socket.listen()

    def start(self):
        logging.info('start')
        threading.Thread(target=self._accept, name='accept', daemon=True).start()

    def stop(self):
        self.event.set()
        time.sleep(3)
        self.socket.close()

    def _accept(self):
        while not self.event.isSet():
            logging.info('accept')

            conn, addr = self.socket.accept()
            self.cients[addr] = conn
            logging.info(conn)
            logging.info(addr)
            threading.Thread(target=self._recv, args=(conn, addr,), name='recv').start()

    def _recv(self, connect, addr):
        print('addr"0', addr)
        while not self.event.isSet():
            try:
                data = connect.recv(1024)
                if data.decode() == 'quit':
                    self.cients.pop(addr)
                    print('now online is {}'.format(len(self.cients)))
                    if len(self.cients) == 0:
                        self.stop()
                else:
                    for client in self.cients.values():
                        if connect is not client:
                            client.send(data)
            except Exception as e:
                logging.info(addr)


# def pp():
#     while not event2.wait(2):
#         logging.info(threading.enumerate())


# if __name__=="__main__":


server = Server('127.0.0.1', 9999)

server.start()

while not server.event.isSet():
    pass