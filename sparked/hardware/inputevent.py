# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Classes dealing with /dev/input/* devices for twisted.

InputEvent class taken from http://github.com/rmt/pyinputevent/
"""

import os
import struct
import time
import ctypes

from twisted.internet import abstract, fdesc, protocol

EV_SYN = 0x00
EV_KEY = 0x01
EV_REL = 0x02
EV_ABS = 0x03
EV_MSC = 0x04
EV_SW = 0x05
EV_LED = 0x11
EV_SND = 0x12
EV_REP = 0x14
EV_FF = 0x15
EV_PWR = 0x16
EV_FF_STATUS = 0x17


__all__ = ['InputEvent', 'InputEventDevice', 'InputEventProtocol']

__voidptrsize = ctypes.sizeof(ctypes.c_voidp)
_64bit = (__voidptrsize == 8)
_32bit = (__voidptrsize == 4)
if _64bit:
    INPUTEVENT_STRUCT = "=LLLLHHl"
    INPUTEVENT_STRUCT_SIZE = 24
elif _32bit: # 32bit
    INPUTEVENT_STRUCT = "=iiHHi"
    INPUTEVENT_STRUCT_SIZE = 16
else:
    raise RuntimeError("Couldn't determine architecture, modify " + __file__ +
                       " to support your system.")


class InputEvent(object):
    """
    A `struct input_event`. You can instantiate it with a buffer, in
    which case the method `unpack(buf)` will be called. Or you can create
    an instance with `InputEvent.new(type, code, value, timestamp=None)`,
    which can then be packed into the structure with the `pack` method.
    """

    __slots__ = ('etype', 'ecode', 'evalue', 'time', 'nanotime')

    def __init__(self, buf=None):
        """By default, unpack from a buffer"""
        if buf:
            self.unpack(buf)

    def set(self, etype, ecode, evalue, timestamp=None):
        """Set the parameters of this InputEvent"""
        if timestamp is None:
            timestamp = time.time()
        self.time, self.nanotime = int(timestamp), int(timestamp%1*1000000.0)
        self.etype = etype
        self.ecode = ecode
        self.evalue = evalue
        return self

    @classmethod
    def new(cls, etype, ecode, evalue, time=None):
        """Construct a new InputEvent object"""
        e = cls()
        e.set(etype, ecode, evalue, time)
        return e

    @property
    def timestamp(self):
        return self.time + (self.nanotime / 1000000.0)

    def unpack(self, buf):
        if _64bit:
            self.time, t1, self.nanotime, t3, \
            self.etype, self.ecode, self.evalue \
            = struct.unpack_from(INPUTEVENT_STRUCT, buf)
        elif _32bit:
            self.time, self.nanotime, self.etype, \
            self.ecode, self.evalue \
            = struct.unpack_from(INPUTEVENT_STRUCT, buf)
        return self
    def pack(self):
        if _64bit:
            return struct.pack(INPUTEVENT_STRUCT,
            self.time, 0, self.nanotime, 0,
            self.etype, self.ecode, self.evalue)
        elif _32bit:
            return struct.pack(INPUTEVENT_STRUCT,
            self.time, self.nanotime,
            self.etype, self.ecode, self.evalue)
    def __repr__(self):
        return "<InputEvent type=%r, code=%r, value=%r>" % \
            (self.etype, self.ecode, self.evalue)
    def __str__(self):
        return "type=%r, code=%r, value=%r" % \
            (self.etype, self.ecode, self.evalue)
    def __hash__(self):
        return hash( (self.etype, self.ecode, self.evalue,) )

    def __eq__(self, other):
        return self.etype == other.etype \
            and self.ecode == other.ecode \
            and self.evalue == other.evalue




class InputEventDevice(abstract.FileDescriptor):
    """
    A select()able, read-only input device from /dev/input/*
    """

    connected = 1

    def __init__(self, protocol, deviceName, reactor):
        abstract.FileDescriptor.__init__(self, reactor)
        self._fileno = os.open(deviceName, os.O_RDONLY | os.O_NONBLOCK)
        self.reactor = reactor
        self.protocol = protocol
        self.protocol.makeConnection(self)
        self.startReading()

    def fileno(self):
        return self._fileno

    def writeSomeData(self, data):
        """
        Write some data to the device.
        """
        raise IOError("Input device is read-only!")

    def doRead(self):
        """
        Some data's readable from serial device.
        """
        return fdesc.readFromFD(self.fileno(), self.protocol.dataReceived)

    def connectionLost(self, reason):
        abstract.FileDescriptor.connectionLost(self, reason)
        os.close(self._fileno)


class InputEventProtocol(protocol.Protocol):
    """
    Receives events from an input device.
    """

    def connectionMade(self):
        self.buf = ""

    def dataReceived(self, data):
        self.buf += data
        while len(self.buf) >= INPUTEVENT_STRUCT_SIZE:
            self.eventReceived(InputEvent(self.buf[:INPUTEVENT_STRUCT_SIZE]))
            self.buf = self.buf[INPUTEVENT_STRUCT_SIZE:]

    def eventReceived(self, event):
        """
        Input event has been received. Override this function to do
        something useful.
        """
        print repr(event)
