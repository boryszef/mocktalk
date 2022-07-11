import click as click

from mocktalk.servers import SSHServer, TelnetServer


@click.command()
@click.option('--telnet-port', default=23, help='Telnet port number')
@click.option('--ssh-port', default=22, help='SSH port number')
@click.argument('rsa_priv_key')
def cli(telnet_port, ssh_port, rsa_priv_key, script=None):
    TelnetServer('', telnet_port, None).start()
    SSHServer(rsa_priv_key, '', ssh_port, None).start()
