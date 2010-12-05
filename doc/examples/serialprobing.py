# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Demonistrating the IProtocolProbe functionality.
"""

from zope.interface import implements

from twisted.python import log
from twisted.internet import protocol, reactor

from sparked.hardware import serialport
from sparked import application


class FooProtocol(protocol.Protocol):
    implements (serialport.IProtocolProbe)

    probeRequest = "\xFF\x00\x01\x83\x84"
    probeResponse = "\xFF\x00\x02\x83\x4E\xD3"


class Application(application.Application):

    def started(self):

        def found(proto, baudrate):
            print "MATCH >>", proto, baudrate

        probe = serialport.SerialProbe("/dev/ttyUSB0")
        probe.addCandidate(FooProtocol, 19200)
        d = probe.start()
        d.addCallbacks(found, log.err)
        d.addCallback(lambda _: reactor.stop())
