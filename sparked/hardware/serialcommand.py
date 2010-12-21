from twisted.internet import protocol


class SerialCommandProtocol(protocol.Protocol):

    commands = {}
    buffer = ""

    def dataReceived(self, data):
        self.buffer += data

        # The minimum size of a response frame is 5 bytes.
        if len(self.buffer) < 5:
            return

        if ord(self.buffer[0]) != 0xFF or ord(self.buffer[1]) != 0:
            #warnings.warn("Invalid response from RFID reader!" + self.readablePackage(self.buffer), InvalidReaderResponse)
            self.buffer = ""
            return

        length = ord(self.buffer[2])

        if len(self.buffer) < length + 4:
            # Not all data has arrived. We have to wait for more data.
            return

        print 1111111

        # do something

        # handle the rest
        self.buffer = self.buffer[4 + length:]
        if self.buffer:
            self.dataReceived(self.buffer)



    def _cmd2logical(self, cmd):
        pass

    def _logical2cmd(self, logical):
        pass
