import socket
import threading
from queue import Queue

import paramiko

from . import logger


class SSHServerInterface(paramiko.ServerInterface):

    def __init__(self):
        self.event_queue = Queue()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED

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

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_shell_request(self, channel):
        self.event_queue.put('shell')
        return True


class SSHClientHandler(threading.Thread):

    def __init__(self, sock, address, rsa_private_key_path):
        super().__init__()
        self.socket = sock
        self.address, self.port = address
        self.rsa_key = paramiko.RSAKey(filename=rsa_private_key_path)
        self.interface = SSHServerInterface()

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
            channel.send(f'\r\n{self.__class__.__name__}:\r\n')
            pipe = channel.makefile("rU")
            data = pipe.readline().strip("\r\n")
            while not data == 'exit':
                data = pipe.readline().strip("\r\n")
                logger.debug(f'[{self.__class__.__name__}] got data on stdin {data}')
        channel.close()
        transport.close()


class SSHServer(threading.Thread):

    def __init__(self, rsa_private_key_path, address='', port=22):
        super().__init__()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((address, port))
        self.server.listen(5)
        self.rsa_private_key_path = rsa_private_key_path

    def run(self):
        while True:
            soc, addr = self.server.accept()
            logger.info(f'[{self.__class__.__name__}] new connection {addr}')
            handler = SSHClientHandler(soc, addr, self.rsa_private_key_path)
            handler.start()
