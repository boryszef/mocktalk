import re

import click as click

from mocktalk.ssh import SSHServer
from mocktalk.telnet import TelnetServer


class Script:
    """Maintain a (question, response) list"""

    def __init__(self, data):
        self.data = [(re.compile(key), value) for key, value in data]

    def match(self, item):
        item = item.decode('UTF-8').strip('\r\n')
        for k, v in self.data:
            if k.match(item):
                return v.encode('UTF-8')
        return None


@click.command()
@click.option('--telnet-port', default=23, help='Telnet port number')
@click.option('--ssh-port', default=22, help='SSH port number')
@click.argument('rsa_priv_key')
@click.argument('script', required=False)
def cli(telnet_port, ssh_port, rsa_priv_key, script=None):
    script_instance = Script(script) if script else []
    TelnetServer('', telnet_port, script_instance).start()
    SSHServer(rsa_priv_key, '', ssh_port, script_instance).start()
