from threading import Lock
from unittest.mock import Mock

from mocktalk.script import Script
from mocktalk.servers import TelnetServer
from mocktalk.telnet import TelnetConnectionHandler


def test_telnet_ip_and_port():
    addr = '127.0.0.1', 3023
    server = TelnetServer(*addr)
    assert server.server.getsockname() == addr


def test_script():
    sock = Mock()
    sock.recv.side_effect = b'foo', b'dummy', b''
    server = TelnetConnectionHandler(
        sock,
        ('127.0.0.1', 2223),
        Script(('foo.*', 'bar')),
        [],
        Lock()
    )
    server.run()
    assert sock.recv.call_count == 3
    sock.send.assert_called_once_with(b'bar')
