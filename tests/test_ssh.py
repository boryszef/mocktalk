from unittest.mock import Mock, patch

from mocktalk.script import Script
from mocktalk.ssh import SSHClientHandler


@patch('paramiko.Transport')
@patch('paramiko.RSAKey')
def test_script(rsa_key, transport):
    transport_instance = transport.return_value
    pipe = Mock()
    pipe.readline.side_effect = b'foo', b'dummy'
    channel = Mock()
    channel.makefile.return_value = pipe
    channel.exit_status_ready.side_effect = False, False, True
    transport_instance.accept.return_value = channel
    server = SSHClientHandler(
        Mock(),
        ('127.0.0.1', 2223),
        Script(('foo.*', 'bar')),
        'rsa_key'
    )
    server.interface.event_queue.put('shell')
    server.run()
    assert pipe.readline.call_count == 2
    channel.send.assert_called_once_with('bar')
