# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Tests for sparked.hardware.serial

Maintainer: Arjan Scherpenisse
"""
from mock import patch
from StringIO import StringIO
from serial.serialutil import SerialException

from twisted.trial import unittest

from zope.interface import implements

from sparked.hardware import serialport


class FakeTransport(StringIO):
    def loseConnection(self):
        pass


class PingPongProtocol:
    implements(serialport.IProtocolProbe)

    probeRequest = "PING"
    probeResponse = "PONG"


class ComplexProtocol:
    implements(serialport.IProtocolProbe)

    probeRequest = "BLEH"
    def probeResponse(self, data):
        return ord(data[0]) + ord(data[1]) == 31



class TestSerialProbe(unittest.TestCase):
    """
    Test the L{sparked.hardware.serialport.SerialProbe}
    """

    def testNone(self):
        probe = serialport.SerialProbe("/dev/null")
        d = probe.start()
        d.addCallback(lambda _: self.fail("Should not have succeeded"))
        d.addErrback(lambda f: self.assertTrue(isinstance(f.value, serialport.SerialProbeException))) # ok
        return d


    def testAddCandidate(self):
        probe = serialport.SerialProbe("/dev/null")
        class Bla:
            pass
        self.assertRaises(serialport.SerialProbeException, probe.addCandidate, Bla, 19200) # does not implement IProtocolProbe
        self.assertRaises(serialport.SerialProbeException, probe.addCandidate, PingPongProtocol, 123) # invalid baud rate
        self.assertEquals(None, probe.addCandidate(PingPongProtocol, 19200)) # all ok


    def testNonExisting(self):
        probe = serialport.SerialProbe("/dev/fdsfdsfds")
        probe.addCandidate(PingPongProtocol, 19200)
        self.assertRaises(SerialException, probe.start)


    @patch('serial.Serial')
    def testSerial(self, Serial):

        # create pipe
        import os
        r, w = os.pipe()

        # patch the serial class to return the file descriptor to our pipe
        inst = Serial.return_value
        inst.fd = r

        # write response in the pipe
        os.write(w, "PONG")

        # perform the test
        probe = serialport.SerialProbe("/dev/some/serial/port")
        probe.addCandidate(PingPongProtocol, 19200)
        d = probe.start()

        d.addCallback(lambda r: self.assertEquals(r, (PingPongProtocol, 19200)))
        d.addCallback(lambda _: os.close(r))
        return d



class TestSerialProbeProtocol(unittest.TestCase):
    """
    Test the L{sparked.hardware.serialport.SerialProbeProtocol}
    """

    def testPingPong(self):
        p = serialport.SerialProbeProtocol(PingPongProtocol())
        d = p.d
        p.transport = FakeTransport()
        p.connectionMade()
        p.dataReceived("PONG")
        d.addCallback(lambda r: self.assertEquals(r, True))
        return d


    def testComplex(self):
        p = serialport.SerialProbeProtocol(ComplexProtocol())
        d = p.d
        p.transport = FakeTransport()
        p.connectionMade()
        p.dataReceived("\x10\x0F")
        d.addCallback(lambda r: self.assertEquals(r, True))
        return d


    def testPingPongFail(self):
        p = serialport.SerialProbeProtocol(PingPongProtocol())
        d = p.d
        p.transport = FakeTransport()
        p.connectionMade()
        p.dataReceived("HEUH")
        d.addCallback(lambda r: self.assertFalse(r))
        return d


    def testPingPongTimeout(self):
        from twisted.internet import task
        clock = task.Clock()

        p = serialport.SerialProbeProtocol(PingPongProtocol(), reactor=clock)
        d = p.d
        p.transport = FakeTransport()
        p.connectionMade()
        p.dataReceived("HE")
        self.assertEquals(False, d.called)
        clock.advance(0.25)
        self.assertEquals(False, d.called)
        clock.advance(0.25)
        d.addCallback(lambda r: self.assertFalse(r))
        return d


    def testPingPongCustomTimeout(self):
        from twisted.internet import task
        clock = task.Clock()

        p = serialport.SerialProbeProtocol(PingPongProtocol(), reactor=clock, timeout=3)
        d = p.d
        p.transport = FakeTransport()
        p.connectionMade()
        p.dataReceived("HE")
        self.assertEquals(False, d.called)
        clock.advance(1.5)
        self.assertEquals(False, d.called)
        clock.advance(1.5)
        d.addCallback(lambda r: self.assertFalse(r))
        return d

