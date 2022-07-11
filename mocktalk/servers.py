import socket
import threading
from typing import List, Union

from mocktalk.telnet import TelnetConnectionHandler
from mocktalk.script import Script
from mocktalk.ssh import SSHClientHandler

from . import logger


TIMEOUT = 5


class MockServerBase(threading.Thread):

    def __init__(self, address: str, port: int, script: Script):
        super().__init__()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((address, port))
        self.server.listen(5)
        self.server.settimeout(TIMEOUT)
        self.script = script
        self.lock = threading.Lock()
        self.clients: List[str] = []
        self.halt_event = threading.Event()

    def run(self):
        while not self.halt_event.is_set():
            handler = self._get_handler()
            if handler is not None:
                handler.start()
        logger.info(f'[{self.__class__.__name__}] Closing socket')
        self.server.close()

    def _get_handler(self):
        try:
            soc, addr = self.server.accept()
        except socket.timeout:
            return None
        logger.info(
            f'[{self.__class__.__name__}] new connection '
            '{addr[0]}:{addr[1]}'
        )
        return self.handler(soc, addr, *self.handler_args)

    def stop(self):
        self.halt_event.set()


class TelnetServer(MockServerBase):

    handler = TelnetConnectionHandler

    def __init__(self, address: str = '', port: int = 23,
                 script: Union[Script, None] = None):
        super().__init__(address, port, script or Script())
        self.handler_args = self.clients, self.lock


class SSHServer(MockServerBase):

    handler = SSHClientHandler

    def __init__(self, rsa_private_key_path: str, address: str = '',
                 port: int = 22, script: Union[Script, None] = None):
        super().__init__(address, port, script or Script())
        self.handler_args = rsa_private_key_path,
