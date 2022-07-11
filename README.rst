########
mocktalk
########

Mock telnet and ssh connections in Python.

What it does
============

This is mostly useful to test code that depends on telnet or ssh connections, for example code that uses telnetlib or pyexpect modules.
It allows to launch an SSH/Telnet test server as a separate thread and define input-response dialogue.

Example of usage
================

.. code-block::

    from mocktalk.script import Script
    from mocktalk.servers import TelnetServer

    script = Script(('foo', 'response1'), ('bar.*baz', 'response2'))
    srv = TelnetServer('127.0.0.1', 2233, script)
    srv.start()


    from telnetlib import Telnet
    tn = Telnet('127.0.0.1', 2233)

    tn.write(b'foo')
    assert tn.read_eager() == b'response1'

    tn.write(b'bar1baz')
    assert tn.read_eager() == b'response2'

Build
=====

To build the package, install `build` module and issue:

`python -m build`

