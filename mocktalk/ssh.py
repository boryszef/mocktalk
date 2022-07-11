import socket
import threading
from queue import Queue
from typing import Tuple

import paramiko

from mocktalk.script import Script

from . import logger


class SSHServerInterface(paramiko.ServerInterface):

    def __init__(self):
        self.event_queue = Queue()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_SUCCESSFUL

    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return 'password,publickey'

    def check_channel_exec_request(self, channel, command):
        self.event_queue.put('command')
        self.event_queue.put(command)
        return True

    def check_channel_pty_request(self, channel, term, width, height,
                                  pixelwidth, pixelheight, modes):
        return True

    def check_channel_shell_request(self, channel):
        self.event_queue.put('shell')
        return True

    def get_banner(self):
        return f'{self.__class__.__name__}\n', 'en-US'


class SSHClientHandler(threading.Thread):

    def __init__(self, sock: socket.socket, address: Tuple[str, int],
                 script: Script, rsa_private_key_path: str):
        super().__init__()
        self.socket = sock
        self.address, self.port = address
        self.rsa_key = paramiko.RSAKey(filename=rsa_private_key_path)
        self.interface = SSHServerInterface()
        self.script = script

    def run(self):
        transport = paramiko.Transport(self.socket)
        transport.set_gss_host(socket.getfqdn(""))
        transport.load_server_moduli()
        transport.add_server_key(self.rsa_key)
        transport.start_server(server=self.interface)
        channel = transport.accept()
        event = self.interface.event_queue.get(timeout=30)
        if event == 'command':
            cmd = self.interface.event_queue.get().decode('UTF-8')
            logger.info(f'[{self.__class__.__name__}] got a command {cmd}')
        elif channel and event == 'shell':
            pipe = channel.makefile('rbU')
            while not channel.exit_status_ready():
                data = pipe.readline()
                match = self.script.match(data)
                if match:
                    channel.send(match.decode('UTF-8'))
                logger.debug(
                    f'[{self.__class__.__name__}] got data on stdin {data}'
                )
            logger.info(
                f'[{self.__class__.__name__}] interactive session closed'
            )
        channel.close()
        transport.close()
