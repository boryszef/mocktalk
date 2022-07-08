import socket
import threading

from . import logger


TIMEOUT = 5


class TelnetConnectionHandler(threading.Thread):

    def __init__(self, sock, address, clients, lock, script):
        super().__init__()
        self.socket = sock
        self.address, self.port = address
        self.clients = clients
        self.lock = lock
        self.script = script

    @property
    def client_name(self):
        return f'{self.address}:{self.port}'

    def run(self):
        self.lock.acquire()
        self.clients.append(self.client_name)
        self.lock.release()

        message = True
        while message:
            message = self.socket.recv(4096)
            match = self.script.match(message)
            if match:
                self.socket.send(match)
            logger.debug(f'[{self.__class__.__name__}] message from {self.client_name}: {message}')

        self.socket.close()
        logger.info(f'[{self.__class__.__name__}] connection from {self.client_name} closed')
        self.lock.acquire()
        self.clients.remove(self.client_name)
        self.lock.release()


class TelnetServer(threading.Thread):

    def __init__(self, address='', port=23, script=None):
        super().__init__()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((address, port))
        self.server.listen(5)
        self.server.settimeout(TIMEOUT)
        self.lock = threading.Lock()
        self.clients = []
        self.script = script
        self.halt_event = threading.Event()

    def run(self):
        while not self.halt_event.is_set():
            try:
                soc, addr = self.server.accept()
            except socket.timeout:
                continue
            logger.info(f'[{self.__class__.__name__}] new connection {addr[0]}:{addr[1]}')
            handler = TelnetConnectionHandler(soc, addr, self.clients, self.lock, self.script).start()
        logger.info(f'[{self.__class__.__name__}] Closing socket')
        self.server.close()

    def stop(self):
        self.halt_event.set()
