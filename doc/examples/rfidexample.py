# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Auto-hot-plug-and-play RFID reader monitor on the serial port.
"""

from twisted.python import log

from sparked.hardware import rfid
from sparked import application


class Application(application.Application):

    def started(self):


        mon = rfid.RFIDMonitor()
        mon.addCandidate(rfid.SL031Protocol, 115200)
        mon.addCandidate(rfid.SonMicroProtocol, 19200)
        mon.setServiceParent(self)

        rfid.rfidEvents.addObserver("tag-added", lambda tag: log.msg("Tag detected!" + str(tag)))


## If you want just one reader, without hot plugging, use the following:
# port = serialport.SerialPort(rfid.SonMicroProtocol(), "/dev/ttyUSB1", reactor, baudrate=19200)
# self.reader = rfid.RFIDReader(port.protocol)
# self.reader.events.addObserver("tag-added", lambda tpe, tag: log.msg("!!!!! "+tag))
