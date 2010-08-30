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

    def testAdd(self):
        self.pinged = 0
        
        class FooMonitor(monitors.Monitor):
            pass

        container = monitors.MonitorContainer()

        def ping(e):
            self.pinged += 1
        container.events.addEventListener(ping)

        container.addMonitor(FooMonitor())
        self.assertEquals(self.pinged, 1)

        container.addMonitor(FooMonitor())
        self.assertEquals(self.pinged, 2)
