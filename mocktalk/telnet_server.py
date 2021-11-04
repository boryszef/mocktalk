import socket
import threading

from . import logger


class TelnetConnectionHandler(threading.Thread):

    def __init__(self, sock, address, clients, lock):
        super().__init__()
        self.socket = sock
        self.address, self.port = address
        self.clients = clients
        self.lock = lock

    @property
    def client_name(self):
        return f'{self.address}:{self.port}'

    def run(self):
        self.lock.acquire()
        self.clients.append(self.client_name)
        self.lock.release()

        while True:
            message = self.socket.recv(4096)
            if not message:
               break
            logger.debug(f'[{self.__class__.__name__}] message from {self.client_name}: {message}')

        self.socket.close()
        logger.info(f'[{self.__class__.__name__}] connection from {self.client_name} closed')
        self.lock.acquire()
        self.clients.remove(self.client_name)
        self.lock.release()


class TelnetServer(threading.Thread):

    def __init__(self, address='', port=23):
        super().__init__()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((address, port))
        self.server.listen(5)
        self.lock = threading.Lock()
        self.clients = []

    def run(self):
        while True:
            soc, addr = self.server.accept()
            logger.info(f'[{self.__class__.__name__}] new connection {addr[0]}:{addr[1]}')
            TelnetConnectionHandler(soc, addr, self.clients, self.lock).start()
