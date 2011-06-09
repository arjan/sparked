# Copyright (c) 2011 Arjan Scherpenisse
# See LICENSE for details.

"""
Tests for sparked.hardware.rfid

Maintainer: Arjan Scherpenisse
"""

import gst

from twisted.trial import unittest

from sparked.hardware import rfid


class FakeTransport(object):
    def __init__(self, c):
        self.c = c
    def write(self, payload):
        self.c.sent = payload
    def flushOutput(self):
        pass

class TestHongChangTagProtocol(unittest.TestCase):

    def setUp(self):
        self.proto = rfid.HongChangTagProtocol()
        self.proto.transport = FakeTransport(self)
        self.sent = ""
        self.recv = ""

    def testSend(self):
        self.proto.sendCommand("LED1", "\x18\x0A")
        self.assertEquals(self.sent, "\x02\x00\x03\x87\x18\x0A\x96\x03")


    def testReceive(self):
        def r(payload):
            self.assertEquals(payload, "\x80")
        self.proto.got_OK = r

        self.proto.dataReceived("\x02\x00\x02\x00\x80\x82\x03")

        self.assertEquals("", self.proto.buffer, "Datagram is not handled entirely")


