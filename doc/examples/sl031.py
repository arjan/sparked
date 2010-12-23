# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Test program for a stronglink SL031 RFID reader.
"""

from twisted.internet import serialport, reactor, task

from sparked.hardware.serialcommand import SerialCommandProtocol
from sparked import application


class SL031Protocol (SerialCommandProtocol):

    sndPreamble = "\xBA"
    rcvPreamble = "\xBD"
    responses = [ ("OK", 0x00),
                  ("NO_TAG", 0x01) ]
    commands = [ ("SELECT", 0x01) ]


    def calculateChecksum(self, payload):
        cksum = 0
        for c in payload:
            cksum = cksum ^ ord(c)
        return cksum


class Application(application.Application):

    def started(self):
        
        self.port = serialport.SerialPort(SL031Protocol(), "/dev/ttyUSB0", reactor, baudrate=115200)

        #def snd():
        self.port.protocol.sendCommand("SELECT")
        #t = task.LoopingCall(snd)
        #t.start(0.2)

