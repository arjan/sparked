# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Tests for sparked.hardware.serialcommand

Maintainer: Arjan Scherpenisse
"""

from twisted.trial import unittest

from sparked.hardware import serialcommand


class MyProto(serialcommand.SerialCommandProtocol):

    commands = [ ('PING', 0x01) ]

    pinged = 0

    def got_PING(self, data):
        self.pinged += 1
        self.lastData = data


class TestSerialCommand(unittest.TestCase):

    def test1(self):
        proto = MyProto()
        proto.dataReceived("\xFF\x00\x02\x01\x03")
        self.assertEquals(proto.pinged, 1)
        self.assertEquals(proto.lastData, "")


    def test2(self):
        proto = MyProto()
        proto.dataReceived("\xFF\x00\x02\x01\x03")
        proto.dataReceived("\xFF\x00\x02\x01\x03")
        self.assertEquals(proto.pinged, 2)
        self.assertEquals(proto.lastData, "")


    def testPartial(self):
        proto = MyProto()
        proto.dataReceived("\xFF\x00")
        proto.dataReceived("\x02\x01\x03\xFF\x00")
        self.assertEquals(proto.pinged, 1)
        self.assertEquals(proto.lastData, "")


    def testWithData(self):
        proto = MyProto()
        proto.dataReceived("\xFF\x00\x03\x01\xAA\xBB\x03")
        self.assertEquals(proto.pinged, 1)
        self.assertEquals(proto.lastData, "\xAA\xBB")
