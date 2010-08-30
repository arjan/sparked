# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Tests for sparked.events.*

Maintainer: Arjan Scherpenisse
"""

from twisted.trial import unittest

from sparked import events

class TestEventGroup(unittest.TestCase):
    """
    Test the L{sparked.events.EventDispatcher}
    """

    def testSimple(self):
        """
        Simple dispatching test
        """
        d = events.EventDispatcher()

        self.count = 0

        def receive():
            self.count += 1
        d.addObserver("hello", receive)

        d.dispatch("hello")
        self.assertEquals(self.count, 1)
        d.dispatch("world")
        self.assertEquals(self.count, 1)
        d.dispatch("hello")
        self.assertEquals(self.count, 2)


    def testArguments(self):
        """
        Test that positional arguments are passed in the event handler
        and that pre-defined positional arguments (after the priority)
        are prepended to the event callback args.
        """
        d = events.EventDispatcher()

        self.args = []

        def receive(*a):
            self.args += a
        d.addObserver("x", receive)

        d.dispatch("x")
        self.assertEquals(self.args, [])

        d.dispatch("x", 3, 3)
        self.assertEquals(self.args, [3, 3])

        self.args = []
        d.addObserver("y", receive, 0, 'yo')
        d.dispatch("y", 3)
        self.assertEquals(self.args, ['yo', 3])
        d.dispatch("y", 4)
        self.assertEquals(self.args, ['yo', 3, 'yo', 4])


    def testKeywordArguments(self):
        """
        Test that the keyword arguments are passed through and that
        predefined keywords arguments are overriden by the keyword
        arguments of the event.
        """
        d = events.EventDispatcher()
        self.kw = {}
        def receive(**kw):
            self.kw.update(kw)

        d.addObserver("x", receive)
        d.dispatch("x")
        self.assertEquals({}, self.kw)

        d.dispatch("x", foo="bar")
        self.assertEquals({'foo': 'bar'}, self.kw)

        self.kw = {}
        d.addObserver("y", receive, foo='bar')
        d.dispatch("y")
        self.assertEquals({'foo': 'bar'}, self.kw)

        d.addObserver("y", receive, foo='bar')
        d.dispatch("y", foo='baz')
        self.assertEquals({'foo': 'baz'}, self.kw)
