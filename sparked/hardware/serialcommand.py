import warnings

from twisted.python import log
from twisted.internet import protocol

from sparked import events


"""
A generalization of a simple, datagram based binary protocol.

Every datagram consists of a preamble to indicate the start of the
packet, followed by a byte with the length of the rest of the payload.
Then the command byte which indicates which command is being executed
(or responded to). Then optionally a data packet, and the datagram is
concluded with a single checksum byte.

The L{SerialCommandProtocol} abstracts above packet handling so that
the preamble and the checksum bytes can be customized for specific
devices.

See L{sparked.hardware.rfid} for a few implementations of this
protocol in RFID readers.
"""



class SerialCommandProtocol(protocol.Protocol):
    """
    @ivar rcvPreamble: String which contains the package header which is expected to be received.
    @ivar sndPreamble: String which contains the package header on outgoing packages.

    """

    commands = []

    rcvPreamble = None
    sndPreamble = None
    lengthIncludesChecksum = None

    logTraffic = False
    logRawTraffic = False

    minPkgLength = None

    events = None


    def __init__(self):
        self.buffer = ""
        self.minPkgLength = len(self.rcvPreamble) + 3
        self.events = events.EventDispatcher()


    def logPackage(self, prefix, package):
        log.msg("%s %s %s" % (repr(self), prefix, self.readablePackage(package)))


    def readablePackage(self, package):
        return "[%s]" % (":".join(["%02X"%(ord(x)) for x in package]))


    def __repr__(self):
        if not self.transport:
            return str(self.__class__)
        return "%s @ %s (%s)" % (self.transport._serial.portstr, self.transport._serial.baudrate, self.__class__)


    def sendCommand(self, logical, data=""):
        payload = self.sndPreamble
        payload += chr(1+len(data)+int(self.lengthIncludesChecksum))
        payload += chr(self._logical2cmd(logical))
        payload += data
        payload += chr(self.calculateChecksum(payload))
        self.transport.write(payload)
        self.transport.flushOutput()
        if self.logTraffic:
            self.logPackage(">>", payload)


    def calculateChecksum(self, payload):
        return sum(map(ord, payload[len(self.sndPreamble):])) % 256


    def dataReceived(self, data):
        if self.logTraffic and self.logRawTraffic:
            self.logPackage("RAW <<", data)

        self.buffer += data

        # The minimum size of a response frame is 5 bytes.
        if len(self.buffer) < self.minPkgLength:
            return

        if self.buffer[:len(self.rcvPreamble)] != self.rcvPreamble:
            warnings.warn("Invalid SerialCommandProtocol response!")
            self.buffer = ""
            return

        length = ord(self.buffer[len(self.rcvPreamble)])

        if not self.lengthIncludesChecksum:
            # need one byte more
            length += 1

        if len(self.buffer) < len(self.rcvPreamble) + 1 + length:
            # Not all data has arrived. We have to wait for more data.
            return

        boundary = len(self.rcvPreamble) + 1 + length

        datagram = self.buffer[:boundary]
        self.datagramReceived(datagram)

        # handle the rest
        self.buffer = self.buffer[boundary:]
        if self.buffer:
            self.dataReceived(self.buffer)


    def datagramReceived(self, datagram):

        if self.logTraffic:
            self.logPackage("<<", datagram)

        i = len(self.rcvPreamble)
        cmdByte = ord(datagram[i+1])
        data = datagram[i+2:-1]
        checksum = ord(datagram[-1])

        calculatedChecksum = self.calculateChecksum(datagram[:-1])

        if checksum != calculatedChecksum:
            warnings.warn("Invalid datagram checksum! %02X != %02X" % (checksum, calculatedChecksum))
            return

        handler = "got_%s" % self._cmd2logical(cmdByte)
        if hasattr(self, handler):
            getattr(self, handler)(data)


    def _cmd2logical(self, cmd):
        return [l for l,c in self.commands if c==cmd][0]


    def _logical2cmd(self, logical):
        return [c for l,c in self.commands if l==logical][0]


