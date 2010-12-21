from twisted.internet import protocol


class SerialCommandProtocol(protocol.Protocol):

    commands = {}
    buffer = ""

    def dataReceived(self, data):
        self.buffer += data

