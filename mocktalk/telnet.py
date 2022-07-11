import socket
import threading
from typing import List, Tuple

from mocktalk.script import Script

from . import logger


class TelnetConnectionHandler(threading.Thread):

    def __init__(self, sock: socket.socket, address: Tuple[str, int],
                 script: Script, clients: List[str], lock: threading.Lock):
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
            logger.debug(
                f'[{self.__class__.__name__}] message from '
                '{self.client_name}: {message}'
            )

        self.socket.close()
        logger.info(
            f'[{self.__class__.__name__}] connection from '
            '{self.client_name} closed'
        )
        self.lock.acquire()
        self.clients.remove(self.client_name)
        self.lock.release()
