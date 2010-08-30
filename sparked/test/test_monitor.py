# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Tests for sparked.monitors.*

Maintainer: Arjan Scherpenisse
"""

from twisted.trial import unittest

from sparked import monitors

class TestEventGroup(unittest.TestCase):
    """
    Test the L{sparked.events.EventGroup}
    """

    def testAddRemove(self):
        self.pinged = 0
        
        class FooMonitor(monitors.Monitor):
            pass

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


