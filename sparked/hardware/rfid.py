from sparked import events



class RFIDReader (object):


    def __init__(self, readerProtocol):
	self.events = events.eventDispatcher()


    def startReading(self):
	pass


    def stopReading(self):
	pass


