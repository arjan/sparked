# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Tests for sparked.hardware.serial

Maintainer: Arjan Scherpenisse
"""

from twisted.trial import unittest

from zope.interface import implements

from sparked.hardware import serialport


class ProtocolA:
    implements(serialport.IProtocolProbe)

    probeRequest = "PING"
    probeResponse = "PONG"



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
        self.assertRaises(serialport.SerialProbeException, probe.addCandidate, ProtocolA, 123) # invalid baud rate
        self.assertEquals(None, probe.addCandidate(ProtocolA, 19200)) # all ok
