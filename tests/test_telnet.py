from threading import Lock
from unittest.mock import Mock

from mocktalk.script import Script
from mocktalk.telnet import TelnetServer, TelnetConnectionHandler


def test_telnet_ip_and_port():
    addr = '127.0.0.1', 3023
    server = TelnetServer(*addr)
    assert server.server.getsockname() == addr


def test_script():
    ip = '127.0.0.1'
    port = 3024
    sock = Mock()
    sock.recv.side_effect = b'foo', b'dummy', b''
    server = TelnetConnectionHandler(
        sock,
        (ip, port),
        [],
        Lock(),
        Script(('foo.*', 'bar'))
    )
    server.run()
    assert sock.recv.call_count == 3
    sock.send.assert_called_once_with(b'bar')
