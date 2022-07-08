from mocktalk.telnet import TelnetServer


def test_telnet_ip_and_port():
    addr = '127.0.0.1', 3023
    server = TelnetServer(*addr)
    assert server.server.getsockname() == addr