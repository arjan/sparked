# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Tests for sparked.monitors.*

Maintainer: Arjan Scherpenisse
"""

from twisted.trial import unittest

from sparked import monitors


class FooMonitor(monitors.Monitor):
    pass


class StatefulMonitor(monitors.Monitor):
    def __init__(self, ok):
        self.ok = ok



class TestMonitorContainer(unittest.TestCase):
    """
    Test the L{sparked.monitors.MonitorContainer}
    """


    def testAddRemove(self):
        c = monitors.MonitorContainer()
        m = FooMonitor()

        self.assertEquals(m.container, None)
        self.assertEquals(c.monitors, [])

        c.addMonitor(m)
        self.assertEquals(m.container, c)
        self.assertEquals(c.monitors, [m])

        c.removeMonitor(m)
        self.assertEquals(m.container, None)
        self.assertEquals(c.monitors, [])



    def testContainerState(self):
        c = monitors.MonitorContainer()

        self.assertEquals(True, c.ok)
        self.assertEquals((), c.state)

        c.addMonitor(StatefulMonitor(True))
        self.assertEquals(True, c.ok)
        self.assertEquals((True,), c.state)

        c.addMonitor(StatefulMonitor(False))
        self.assertEquals(False, c.ok)
        self.assertEquals((True, False), c.state)


    def testContainerStateNone(self):
        c = monitors.MonitorContainer()
        c.addMonitor(StatefulMonitor(None))
        self.assertEquals(True, c.ok)
        self.assertEquals((None,), c.state)


    def testSignals(self):
        """
        Whether the "updated" signal comes in when a monitor changes state.
        """
        self.pinged = 0
        
        container = monitors.MonitorContainer()

        def ping(c):
            self.pinged += 1
            self.assertEquals(c, container)

        container.events.addObserver("updated", ping)

        a = FooMonitor()
        container.addMonitor(a)
        self.assertEquals(self.pinged, 1)
        self.assertEquals(container.monitors, [a])
        
        b = FooMonitor()
        container.addMonitor(b)
        self.assertEquals(self.pinged, 2)
        self.assertEquals(container.monitors, [a, b])

        container.removeMonitor(a)
        self.assertEquals(self.pinged, 3)
        self.assertEquals(container.monitors, [b])


    def testRemoveNonExisting(self):
        ca = monitors.MonitorContainer()
        self.assertRaises(ValueError, ca.removeMonitor, FooMonitor())


    def testAddToOther(self):
        """
        Whether the "updated" signal comes in when a monitor changes state.
        """

        ca = monitors.MonitorContainer()
        cb = monitors.MonitorContainer()

        m = FooMonitor()
        ca.addMonitor(m)
        self.assertEquals(ca.monitors, [m])
        self.assertEquals(cb.monitors, [])
        cb.addMonitor(m)
        self.assertEquals(ca.monitors, [])
        self.assertEquals(cb.monitors, [m])
