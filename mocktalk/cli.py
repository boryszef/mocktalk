import click as click

from mocktalk.ssh_server import SSHServer
from mocktalk.telnet_server import TelnetServer


@click.command()
@click.option('--telnet-port', default=23, help='Telnet port number')
@click.option('--ssh-port', default=22, help='SSH port number')
@click.argument('rsa_priv_key')
def cli(telnet_port, ssh_port, rsa_priv_key):
    TelnetServer('', telnet_port).start()
    SSHServer(rsa_priv_key, '', ssh_port).start()
