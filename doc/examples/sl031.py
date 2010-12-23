# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Test program for a stronglink SL031 RFID reader.
"""

from zope.interface import implements

from twisted.python import log
from twisted.internet import serialport, reactor, task

from sparked.hardware.serialcommand import SerialCommandProtocol
from sparked.hardware.serialport import IProtocolProbe, SerialProbe, SerialPortMonitor

from sparked import application


class SL031Protocol (SerialCommandProtocol):
    implements (IProtocolProbe)

    probeRequest = "\xBA\x02\x01\xB9"
    probeResponse = "\xBD\x03\x01\x01\xBE"

    sndPreamble = "\xBA"
    rcvPreamble = "\xBD"
    lengthIncludesChecksum = True

    commands = [ ("SELECT", 0x01) ]

    #logTraffic = True

    def calculateChecksum(self, payload):
        cksum = 0
        for c in payload:
            cksum = cksum ^ ord(c)
        return cksum

    def got_SELECT(self, data):
	self.logPackage("SELECT", data)


class SonmicroProtocol (SerialCommandProtocol):
    implements (IProtocolProbe)

    probeRequest = "\xFF\x00\x01\x83\x84"
    probeResponse = "\xFF\x00\x02\x83\x4E\xD3"

    sndPreamble = "\xFF\x00"
    rcvPreamble = "\xFF\x00"
    lengthIncludesChecksum = False

    commands = [ ("SELECT", 0x83) ]

    #logTraffic = True

    def got_SELECT(self, data):
	self.logPackage("SELECT", data)



class RFIDMonitor (SerialPortMonitor):

    def deviceAdded(self, info):
	d = info['device']
	print info
	print "added:", d
	reactor.callLater(1, self.probe, d)


    def probe(self, device):
        probe = SerialProbe(device)
        probe.addCandidate(SonmicroProtocol, 19200)
        probe.addCandidate(SL031Protocol, 115200)
        d = probe.start()
	d.addCallbacks(lambda r: self.found(device, r[0], r[1]), log.err)
        #d.addCallback(lambda _: reactor.stop())


    def found(self, device, proto, baudrate):
	print "MATCH >>", proto, baudrate
	port = serialport.SerialPort(proto(), device, reactor, baudrate=baudrate)
	def snd():
	    port.protocol.sendCommand("SELECT")
	task.LoopingCall(snd).start(0.3)




class Application(application.Application):

    def started(self):

	RFIDMonitor().setServiceParent(self)

