# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
RFID readers which work over serial.
"""


from zope.interface import implements, Interface, Attribute

from twisted.internet import task
from twisted.python import log

from sparked.hardware.serialcommand import SerialCommandProtocol
from sparked.hardware.serialport import IProtocolProbe

from sparked.events import EventDispatcher


events = EventDispatcher()


class TagType:
    UNKNOWN = "Unknown"
    MIFARE_1K = "Mifare_1k"
    MIFARE_4K = "Mifare_4k"
    MIFARE_ULTRALIGHT = "Mifare_ultralight"



class IRFIDReaderProtocol(Interface):

    events = Attribute(
        """
        An L{sparked.events.EventDispatcher} object. Implements the
        following events:

        'tag-present' with kwargs: type=<tag type>, serial=<serial> -
        every time a tag is polled.
        """)

    def start():
        """ Start polling/seeking for tags. """

    def stop():
        """ Stop polling/seeking for tags. """



class SL031Protocol (SerialCommandProtocol):
    implements (IProtocolProbe, IRFIDReaderProtocol)

    # IProtocolProbe variables
    probeRequest = "\xBA\x02\x01\xB9"
    probeResponse = "\xBD\x03\x01\x01\xBE"

    # SerialCommandProtocol variables
    sndPreamble = "\xBA"
    rcvPreamble = "\xBD"
    lengthIncludesChecksum = True

    commands = [ ("SELECT", 0x01) ]

    pollInterval = 0.2



    def calculateChecksum(self, payload):
        return reduce(lambda a,b: a^b, [ord(c) for c in payload])


    def got_SELECT(self, data):
        self.logPackage("SELECT", data)
        self.events.dispatch("tag-present", TagType.UNKNOWN, "DEADBEEF")


    def start(self):
        self._poller = task.LoopingCall(self.sendCommand, "SELECT")
        self._poller.start(self.pollInterval)


    def stop(self):
        self._poller.stop()



class SonMicroProtocol (SerialCommandProtocol):
    implements (IProtocolProbe, IRFIDReaderProtocol)

    probeRequest = "\xFF\x00\x01\x83\x84"
    probeResponse = "\xFF\x00\x02\x83\x4E\xD3"

    sndPreamble = "\xFF\x00"
    rcvPreamble = "\xFF\x00"
    lengthIncludesChecksum = False

    commands = [ ("SELECT", 0x83),
                 ("FIRMWARE", 0x81) ]

    pollInterval = 0.2

    logTraffic = False

    typemap = {0x01: TagType.MIFARE_ULTRALIGHT,
               0x02: TagType.MIFARE_1K,
               0x03: TagType.MIFARE_4K,
               0xFF: TagType.UNKNOWN}


    def got_FIRMWARE(self, data):
        log.msg("%s - Firmware: %s" % (repr(self), data))


    def got_SELECT(self, data):
        if data == "N":
            # no tag present
            return
        if data == "U":
            # RF field off
            return
        tagtype = self.typemap[ord(data[0])]
        tag = "".join("%02X" % ord(c) for c in data[1:])
        self.events.dispatch("tag-present", tagtype, tag)


    def start(self):
        self._poller = task.LoopingCall(self.sendCommand, "SELECT")
        self._poller.start(self.pollInterval)


    def stop(self):
        self._poller.stop()



class RFIDReader (object):

    timeout = 0.5
    reactor = None
    protocol = None

    def __init__(self, protocol, reactor=None):
        assert IRFIDReaderProtocol.implementedBy(protocol.__class__)

        self.events = EventDispatcher()
        self.events.setEventParent(events)

        self.protocol = protocol
        self.protocol.events.addObserver("tag-present", self.gotTag)
        self.protocol.events.setEventParent(self.events)

        self.protocol.start()

        self.tags = {}
        if reactor is None:
            from twisted.internet import reactor
        self.reactor = reactor


    def _tagTimeout(self, tpe, tag):
        self.events.dispatch("tag-removed", tpe, tag)
        del self.tags[tag]


    def gotTag(self, tpe, tag):
        if tag in self.tags:
            return self.tags[tag].reset(self.timeout)
        self.tags[tag] = self.reactor.callLater(self.timeout, self._tagTimeout, tpe, tag)
        self.events.dispatch("tag-added", tpe, tag)
