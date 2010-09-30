# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Demonistrating the IProtocolProbe functionality.
"""

import sys

from zope.interface import implements

from twisted.python import log
from twisted.internet import protocol, reactor

from sparked.hardware import serial


if __name__ == "__main__":

    class FooProtocol(protocol.Protocol):
        implements (serial.IProtocolProbe)

        probeRequest = "\xFF\x00\x01\x83\x84"
        probeResponse = "\xFF\x00\x02\x83\x4E\xD3"



    def pr(*a):
        print ">>", a
        reactor.stop()

    log.startLogging(sys.stdout)


    probe = serial.SerialProbe("/dev/ttyUSB0")
    probe.addCandidate(FooProtocol, 19200)
    d = probe.start()

    d.addBoth(pr)
    
    reactor.run()

