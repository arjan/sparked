# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Everything serial ports.

Autodetection of plugged in serialport devices and protocol probing.
"""


from zope.interface import Interface, Attribute

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

    def deviceAdded(self, udi):
        device = hal.HardwareMonitor.deviceAdded(self, udi)
        if not device:
            return
        log.msg("Serial port found: %s" % self.deviceInfo[udi]["unique_path"])
        self.serialPortAdded(udi, self.deviceInfo[udi])


    def deviceRemoved(self, udi):
        if udi in self.deviceInfo:
            self.serialPortRemoved(udi, self.deviceInfo[udi])
        hal.HardwareMonitor.deviceRemoved(self, udi)


    def serialPortAdded(self, udi, info):
        serialEvents.dispatch("serialport-added", udi=udi, info=info)


    def serialPortRemoved(self, udi, info):
        serialEvents.dispatch("serialport-removed", udi=udi, info=info)


serialEvents = events.EventDispatcher()
""" Event dispatcher for serial events """


class IProtocolProbe(Interface):

    probeRequest = Attribute("""
        What to send to the serial port on connection.
        """)
    
    probeResponse = Attribute("""
        What to receive from the serial port. When this is a string,
        the serialport is expected to return exactly this.

        If this attribute is callable as staticmethod(), a boolean
        return value determines whether the probe is successful or
        not. If None is returned, there is not enough data yet and the
        function will be called again when data arrives again.
        """)



class SerialProbeFactory(object):
    pass





class SerialProbe(object):

    def __init__(self, device):
        self.candidates = []
        self.device = device
        

    def addCandidate(self, proto, baudrate=9600):
        if not IProtocolProbe.implementedBy(proto):
            raise Exception("%s should implement IProtocolProbe" % proto)

        self.candidates.append( (proto, baudrate) )


    def start(self):
        self.deferred = defer.Deferred()
        self._next()
        return self.deferred
    

    def _next(self):
        probe, baudrate = self.candidates[0]
        del self.candidates[0]

        print "Trying", probe
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

        self.deferred.errback(Exception("Probing failed"))



class SerialProbeProtocol(protocol.Protocol):
    def __init__(self, probe, timeout=0.5):
        self.probe = probe
        self.timeout = timeout
        self.d = defer.Deferred()

    def connectionMade(self):
        self.data = ""
        self.transport.write(self.probe.probeRequest)
        self.timer = reactor.callLater(self.timeout, self.response, False)

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
