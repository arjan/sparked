# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Tests for blurb.events.*

Maintainer: Arjan Scherpenisse
"""

from twisted.trial import unittest

from blurb import events

class TestEventGroup(unittest.TestCase):
    """
    Test the L{dispatch.AddressNode}; adding/removing/dispatching callbacks, wildcard matching.
    """

    def testGroup(self):

        g = events.EventGroup()

        rcv = []

        @g.receiveEvents()
        def receive(e):
            rcv.append(e)

        g.sendEvent("hello")
        self.assertEquals(rcv, ["hello"])
        g.sendEvent("world")
        self.assertEquals(rcv, ["hello", "world"])


    def testGroupFiltering(self):
        g = events.EventGroup()

        rcv = []

        @g.receiveEvents()
        def receive(e):
            rcv.append(e)

        class MyEvent(events.Event):
            pass

        @g.receiveEvents(MyEvent)
        def receive1(e):
            rcv.append(e)

        g.sendEvent("hello")
        self.assertEquals(rcv, ["hello"])
        g.sendEvent("world")
        self.assertEquals(rcv, ["hello", "world"])

        ev = MyEvent()
        g.sendEvent(ev)
        self.assertEquals(rcv, ["hello", "world", ev, ev])
 


    def testEvent(self):
        self.assertEquals(events.Event(foo="bar"), events.Event(foo="bar"))
        self.assertNotEquals(events.Event(foo="bar", baz="hi"), events.Event(foo="bar"))
