import warnings

from twisted.internet import protocol


class SerialCommandProtocol(protocol.Protocol):
    """

    @ivar rcvPreamble: String which contains the package header which is expected to be received.
    @ivar sndPreamble: String which contains the package header which is expected to be received.

    """

    commands = []
    responses = []

    rcvPreamble = "\xFF\x00"
    sndPreamble = "\xFF\x00"

    minPkgLength = None


    def __init__(self):
        self.buffer = ""
        self.minPkgLength = len(self.rcvPreamble) + 3


    def readablePackage(self, data):
        return "[%s]" % (":".join(["%02X"%(ord(x)) for x in data]))


    def sendCommand(self, logical, data=""):
        payload = self.sndPreamble
        payload += chr(2+len(data))
        payload += chr(self._logical2cmd(logical))
        payload += data
        payload += chr(self.calculateChecksum(payload))
        self.transport.write(payload)
        self.transport.flushOutput()
        print ">>", self.readablePackage(payload)


    def calculateChecksum(self, payload):
        return chr(sum(map(ord, payload[len(self.sndPreamble):])) % 256)

    def dataReceived(self, data):
        print "YOOOO"
        self.buffer += data

        # The minimum size of a response frame is 5 bytes.
        if len(self.buffer) < self.minPkgLength:
            return

        if self.buffer[:len(self.rcvPreamble)] != self.rcvPreamble:
            warnings.warn("Invalid SerialCommandProtocol response!")
            self.buffer = ""
            return

        length = ord(self.buffer[2])

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
        # strip preamble
        datagram = datagram[len(self.rcvPreamble):]
        
        length = ord(datagram[0])
        rspByte = ord(datagram[1])
        data = datagram[2:-1]
        checksum = ord(datagram[-1])

        calculatedChecksum = (length + rspByte + sum(map(ord, data))) % 256

        if checksum != calculatedChecksum:
            warnings.warn("Invalid datagram checksum!")
            return

        handler = "got_%s" % self._rsp2logical(rspByte)
        if hasattr(self, handler):
            getattr(self, handler)(data)


    def _rsp2logical(self, cmd):
        return [l for l,c in self.responses if c==cmd][0]


    def _logical2rsp(self, logical):
        return [c for l,c in self.responses if l==logical][0]


    def _cmd2logical(self, cmd):
        return [l for l,c in self.commands if c==cmd][0]


    def _logical2cmd(self, logical):
        return [c for l,c in self.commands if l==logical][0]


