# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Everything serial ports.

Autodetection of plugged in serialport devices and protocol probing.
"""


from zope.interface import Interface, Attribute

import serial

from twisted.python import log
from twisted.internet import protocol, defer, reactor
from twisted.internet.serialport import SerialPort

from sparked.hardware import hal
from sparked import events


class SerialPortMonitor (hal.HardwareMonitor):
    """
    Serial port device monitor.
    """
    subsystem = "serial"

    def __init__(self):
        self.events = serialEvents

serialEvents = events.EventDispatcher()
""" Global event dispatcher for all serial events """


class IProtocolProbe(Interface):

    probeRequest = Attribute("""
        What to send to the serial port on connection.
        """)

    probeResponse = Attribute("""
        What to receive from the serial port. When this is a string,
        the serialport is expected to return exactly this.

        If this attribute is callable as a static method, a boolean
        return value determines whether the probe is successful or
        not. If None is returned, there is not enough data yet and the
        function will be called again when data arrives again.
        """)



class SerialProbeException (Exception):
    pass



class SerialProbe(object):
    """
    Request/response-based serial device fingerprinting. Given a
    serial device, try a series of protocol+baudrate combinations to
    see if they match.
    """

    def __init__(self, device):
        self.candidates = []
        self.device = device
        

    def addCandidate(self, proto, baudrate=9600):
        if not IProtocolProbe.implementedBy(proto):
            raise SerialProbeException("%s should implement IProtocolProbe" % proto)
        if baudrate not in serial.baudrate_constants.keys():
            raise SerialProbeException("Invalid baud rate: %d" % baudrate)

        self.candidates.append( (proto, baudrate) )


    def start(self):
        self.deferred = defer.Deferred()
        if not self.candidates:
            return defer.fail(SerialProbeException("No protocols to probe"))
        self._next()
        return self.deferred
        
    

    def _next(self):
        probe, baudrate = self.candidates[0]
        del self.candidates[0]

        log.msg("Trying %s @ %d baud" % (probe, baudrate))
        proto = SerialProbeProtocol(probe)
        try:
            SerialPort(proto, self.device, reactor, baudrate=baudrate)
        except:
            # "port not open"
            self._probeResult(False, probe, baudrate)
            return

        proto.d.addCallback(self._probeResult, probe, baudrate)


    def _probeResult(self, r, probe, baudrate):
        if r is True:
            self.deferred.callback( (probe, baudrate) )
            return

        if len(self.candidates):
            self._next()
            return

        self.deferred.errback(SerialProbeException("Probing failed"))



class SerialProbeProtocol(protocol.Protocol):
    """
    Internal protocol which tries if given IProtocolProbe fits the
    current connection.
    """

    def __init__(self, probe, timeout=0.5, reactor=None):
        if not reactor:
            from twisted.internet import reactor
        self.reactor = reactor
        self.probe = probe
        self.timeout = timeout
        self.d = defer.Deferred()


    def connectionMade(self):
        self.data = ""
        self.transport.write(self.probe.probeRequest)
        self.timer = self.reactor.callLater(self.timeout, self.response, False)


    def dataReceived(self, data):
        self.data += data

        if callable(self.probe.probeResponse):
            retval = self.probe.probeResponse(self.data)
        else:
            if len(self.data) < len(self.probe.probeResponse):
                retval = None
            else:
                retval = self.probe.probeResponse == self.data[:len(self.probe.probeResponse)]
        if retval is None:
            return

        self.response(retval)

    def response(self, val):
        if self.timer.active():
            self.timer.cancel()
        self.transport.loseConnection()
        self.d.callback(val)
