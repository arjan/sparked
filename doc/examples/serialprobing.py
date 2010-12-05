# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Demonistrating the IProtocolProbe functionality.
"""

from zope.interface import implements

from twisted.python import log
from twisted.internet import protocol, reactor

import sparked.hardware.serial
from sparked import application



class FooProtocol(protocol.Protocol):
#    implements (serial.IProtocolProbe)

    probeRequest = "\xFF\x00\x01\x83\x84"
    probeResponse = "\xFF\x00\x02\x83\x4E\xD3"


class Application(application.Application):

    def started(self):

        def found(proto, baudrate):
            print ">>", proto, baudrate
            reactor.stop()

        probe = sparked.hardware.serial.SerialProbe("/dev/ttyUSB0")
        probe.addCandidate(FooProtocol, 19200)
        d = probe.start()
        d.addCallbacks(found, log.err)
