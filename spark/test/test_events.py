# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Tests for spark.events.*

Maintainer: Arjan Scherpenisse
"""

from twisted.trial import unittest

from spark import events

class TestEventGroup(unittest.TestCase):
    """
    Test the L{spark.events.EventGroup}
    """

    def testGroup(self):

        g = events.EventGroup()

        rcv = []

        def receive(e):
            rcv.append(e)
        g.addEventListener(receive)

        g.sendEvent("hello")
        self.assertEquals(rcv, ["hello"])
        g.sendEvent("world")
        self.assertEquals(rcv, ["hello", "world"])


    def testGroupFiltering(self):
        g = events.EventGroup()

        rcv = []

        def receive(e):
            rcv.append(e)
        g.addEventListener(receive)

        class MyEvent(events.Event):
            pass

        def receive1(e):
            rcv.append(e)
        g.addEventListener(receive, MyEvent)

        g.sendEvent("hello")
        self.assertEquals(rcv, ["hello"])
        g.sendEvent("world")
        self.assertEquals(rcv, ["hello", "world"])

        ev = MyEvent()
        g.sendEvent(ev)
        self.assertEquals(rcv, ["hello", "world", ev, ev])
 


    def testGroupInstance(self):

        g = events.EventGroup()

        class MyEvent(events.Event):
            pass

        class Receiver:

            def __init__(self):
                self.rcv = []
                g.addEventListener(self.receive)
                g.addEventListener(self.receive2, MyEvent)

            def receive(self, e):
                self.rcv.append(e)

            def receive2(self, e):
                self.rcv.append(e)

        r = Receiver()

        g.sendEvent("hello")
        self.assertEquals(r.rcv, ["hello"])

        g.sendEvent(MyEvent())
        self.assertEquals(r.rcv, ["hello", MyEvent(), MyEvent()])



class TestEvent(unittest.TestCase):
    """
    Test the L{spark.events.Event}
    """

    def testEquality(self):
        self.assertEquals(events.Event(foo="bar"), events.Event(foo="bar"))
        self.assertNotEquals(events.Event(foo="bar", baz="hi"), events.Event(foo="bar"))

