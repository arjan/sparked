# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Tests for sparked.application.*

Maintainer: Arjan Scherpenisse
"""
import tempfile
import os

from twisted.trial import unittest
from twisted.internet import task

from sparked.events import EventDispatcher
from sparked.monitors import MonitorContainer
from sparked.application import getPath, Options, Application, StateMachine


class TestGetPath(unittest.TestCase):
    """
    Test the L{application.getPath}
    """

    def testInvalidPath(self):
        self.assertRaises(ValueError, getPath, "someinvalidpath", "", {})


    def testTempPath(self):
        self.assertEqual("/tmp/foo", getPath("temp", "foo", {}).path)
        self.assertEqual("/tmp/bar", getPath("temp", "foo", {'id': 'bar'}).path)
        self.assertEqual("/beh/dinges", getPath("temp", "foo", {'temp-path': '/beh/dinges'}).path)
        self.assertEqual("/tmp/foo", getPath("temp", "foo", {'system-paths': True}).path)


    def testLogPath(self):
        self.assertEqual("/tmp/foo/sparkd.log", getPath("logfile", "foo", {}).path)
        self.assertEqual("/tmp/bar/sparkd.log", getPath("logfile", "foo", {'id': 'bar'}).path)
        self.assertEqual("/beh/dinges/sparkd.log", getPath("logfile", "foo", {'temp-path': '/beh/dinges'}).path)
        self.assertEqual("/aap.log", getPath("logfile", "foo", {'logfile': '/aap.log'}).path)
        self.assertEqual("/aap.log", getPath("logfile", "foo", {'logfile': '/aap.log', 'system-paths': True}).path)
        self.assertEqual("/var/log/foo.log", getPath("logfile", "foo", {'system-paths': True}).path)
        self.assertEqual("/var/log/bar.log", getPath("logfile", "foo", {'system-paths': True, 'id': 'bar'}).path)


    def testPidPath(self):
        self.assertEqual("/tmp/foo/sparkd.pid", getPath("pidfile", "foo", {}).path)
        self.assertEqual("/tmp/bar/sparkd.pid", getPath("pidfile", "foo", {'id': 'bar'}).path)
        self.assertEqual("/beh/dinges/sparkd.pid", getPath("pidfile", "foo", {'temp-path': '/beh/dinges'}).path)
        self.assertEqual("/aap.pid", getPath("pidfile", "foo", {'pidfile': '/aap.pid'}).path)
        self.assertEqual("/aap.pid", getPath("pidfile", "foo", {'pidfile': '/aap.pid', 'system-paths': True}).path)
        self.assertEqual("/var/run/foo.pid", getPath("pidfile", "foo", {'system-paths': True}).path)
        self.assertEqual("/var/run/bar.pid", getPath("pidfile", "foo", {'system-paths': True, 'id': 'bar'}).path)


    def testDataPath(self):
        c = os.getcwd()
        self.assertEqual(c+"/data", getPath("data", "foo", {}).path)
        self.assertEqual(c+"/data", getPath("data", "foo", {'id': 'bar'}).path)
        self.assertEqual(c+"/data", getPath("data", "foo", {'temp-path': '/beh/dinges'}).path)
        self.assertEqual("/var/aap", getPath("data", "foo", {'data-path': '/var/aap/'}).path)
        self.assertEqual("/var/aap", getPath("data", "foo", {'data-path': '/var/aap/', 'system-paths': True}).path)
        self.assertEqual("/usr/share/foo", getPath("data", "foo", {'system-paths': True}).path)
        self.assertEqual("/usr/share/foo", getPath("data", "foo", {'system-paths': True, 'id': 'bar'}).path)


    def testDBPath(self):
        self.assertEqual("/tmp/foo/db", getPath("db", "foo", {}).path)
        self.assertEqual("/tmp/bar/db", getPath("db", "foo", {'id': 'bar'}).path)
        self.assertEqual("/beh/dinges/db", getPath("db", "foo", {'temp-path': '/beh/dinges'}).path)
        self.assertEqual("/var/aap", getPath("db", "foo", {'db-path': '/var/aap/'}).path)
        self.assertEqual("/var/aap", getPath("db", "foo", {'db-path': '/var/aap/', 'system-paths': True}).path)
        self.assertEqual("/var/lib/foo", getPath("db", "foo", {'system-paths': True}).path)
        self.assertEqual("/var/lib/bar", getPath("db", "foo", {'system-paths': True, 'id': 'bar'}).path)


    def testPathExpansion(self):
        self.assertEqual(os.getenv("HOME"), getPath("data", "foo", {"data-path": "~"}).path)
        self.assertEqual(os.getenv("HOME")+"/tmp", getPath("data", "foo", {"data-path": "~/tmp"}).path)



class TestApplicationOptions(unittest.TestCase):

    def testSaveLoad(self):
        class TestOpts(Options):
            optFlags = [["fast", "f", "Run fast"]]
            optParameters = [["user", "u", None, "The user name"]]
        fn = tempfile.mkstemp()[1]
        opta = TestOpts()
        opta.parseOptions(["-f", "-u", "arjan"])
        opta.save(fn)

        optb = TestOpts.load(fn)
        self.assertEquals(opta['fast'], optb['fast'])
        self.assertEquals(opta['user'], optb['user'])


    def testSaveLoadComplex(self):
        class TestOptsComplex(Options):
            verboseCalled = False
            def opt_verbose(self):
                self.verboseCalled = True
                self['verbose'] = True

        fn = tempfile.mkstemp()[1]
        opta = TestOptsComplex()
        opta.parseOptions(["--verbose"])
        opta.save(fn)

        optb = TestOptsComplex.load(fn)
        self.assertEquals(opta['verbose'], True)
        self.assertEquals(opta['verbose'], optb['verbose'])
        self.assertEquals(optb.verboseCalled, True)

        opta['verbose'] = False
        opta.save(fn)
        optb = TestOptsComplex.load(fn)
        self.assertEquals(optb['verbose'], False)
        self.assertEquals(optb.verboseCalled, False)


    def testSaveLoadCallback(self):
        class TestOptsComplex2(Options):
            def opt_foo(self, arg):
                if arg != "bar":
                    raise ValueError("foo must be bar")
                self['foo'] = arg
        fn = tempfile.mkstemp()[1]
        opta = TestOptsComplex2()
        opta.parseOptions(["--foo=bar"])
        opta['foo'] = 'baz'
        opta.save(fn)
        self.assertRaises(ValueError, TestOptsComplex2.load, fn)


    def testSaveLoadTypeEnforcement(self):

        class TestOptsComplex3(Options):
            optParameters = [["count", "c", None, "The count", int]]
        fn = tempfile.mkstemp()[1]
        opta = TestOptsComplex3()
        opta.parseOptions(["--count=11"])
        opta['count'] = 'not_a_number'
        opta.save(fn)
        self.assertRaises(ValueError, TestOptsComplex3.load, fn)



class TestApplication(unittest.TestCase):
    """
    Test the L{sparked.application.Application} class.
    """

    def testConstructor(self):
        """
        Test if all assignments in the application constructor are set.
        """
        app = Application("foo", {}, {})
        self.assertEquals("foo", app.appId)
        self.assertEquals({}, app.appOpts)
        self.assertEquals({}, app.baseOpts)

        self.assertIsInstance(app.state, StateMachine)
        self.assertTrue(app.state.verbose)
        self.assertIsInstance(app.events, EventDispatcher)
        self.assertIsInstance(app.monitors, MonitorContainer)


    def testConstructorStartupOrder(self):
        seq = []
        class TestApp(Application):
            def starting(app):
                seq.append("starting")
                self.assertEquals(None, app.state.get)

            def started(app):
                seq.append("started")
                self.assertEquals("start", app.state.get)

        clock = task.Clock()

        TestApp("foo", {}, {}, reactor=clock)
        clock.advance(0.1)

        self.assertEquals(seq, ["starting", "started"])


    def testConstructorStartupCrash(self):
        """ The L{application.started} call may crash """
        self.stopped = False

        class TestApp(Application):
            def starting(app):
                raise ValueError("Whoooops")

        class StoppableClock(task.Clock):
            def stop(s):
                self.stopped = True
        clock = StoppableClock()

        TestApp("foo", {}, {}, reactor=clock)
        clock.advance(0.5)
        self.assertEquals(1, len(self.flushLoggedErrors(ValueError)))
        self.assertTrue(self.stopped, "Reactor need to be stopped on startup error")


    def testConstructorStartupCrash2(self):
        """ The L{application.started} call may crash as well """
        self.stopped = False

        class TestApp(Application):
            def started(app):
                raise ValueError("Whoooops")

        class StoppableClock(task.Clock):
            def stop(s):
                self.stopped = True
        clock = StoppableClock()

        TestApp("foo", {}, {}, reactor=clock)
        clock.advance(0.5)
        self.assertEquals(1, len(self.flushLoggedErrors(ValueError)))
        self.assertTrue(self.stopped, "Reactor need to be stopped on startup error")



class TestStateMachine(unittest.TestCase):

    def testConstruct(self):
        m = StateMachine(None)
        self.assertEquals(None, m.get)
        self.assertFalse(m.verbose)


    def testGetSet(self):
        m = StateMachine(None)
        m.set("foo")
        self.assertEquals("foo", m.get)


    def testSetAfter(self):
        clock = task.Clock()
        m = StateMachine(None, reactor=clock)
        m.setAfter("foo", 1.0)
        self.assertEquals(None, m.get)
        clock.advance(1.0)
        self.assertEquals("foo", m.get)


    def testSetAfterCancelled(self):
        clock = task.Clock()
        m = StateMachine(None, reactor=clock)
        m.setAfter("foo", 1.0)
        self.assertEquals(None, m.get)
        clock.advance(0.5)
        m.set("bar")
        clock.advance(0.5)
        self.assertEquals("bar", m.get)


    def testBumpAfter(self):
        clock = task.Clock()
        m = StateMachine(None, reactor=clock)
        m.setAfter("foo", 1.0)
        self.assertEquals(None, m.get)
        clock.advance(0.5)
        m.bumpAfter()
        clock.advance(0.5)
        self.assertEquals(None, m.get)
        clock.advance(0.5)
        self.assertEquals("foo", m.get)


    def testBumpAfter2(self):
        clock = task.Clock()
        m = StateMachine(None, reactor=clock)
        m.setAfter("foo", 1.0)
        self.assertEquals(None, m.get)
        clock.advance(0.5)
        m.bumpAfter()
        clock.advance(0.5)
        self.assertEquals(None, m.get)
        m.bumpAfter()
        clock.advance(0.5)
        self.assertEquals(None, m.get)
        clock.advance(0.5)
        self.assertEquals("foo", m.get)


    def testCallbacks(self):
        self.called = []
        class Listener:
            def enter_a(s): self.called.append("enter_a")
            def exit_a(s): self.called.append("exit_a")
            def enter_b(s): self.called.append("enter_b")
            def exit_b(s): self.called.append("exit_b")
        m = StateMachine(Listener())
        m.set("a")
        self.assertEquals(self.called, ["enter_a"])

        m.set("a")
        self.assertEquals(self.called, ["enter_a", "exit_a", "enter_a"])

        m.set("b")
        self.assertEquals(self.called, ["enter_a", "exit_a", "enter_a", "exit_a", "enter_b"])

        m.set("a")
        self.assertEquals(self.called, ["enter_a", "exit_a", "enter_a", "exit_a", "enter_b", "exit_b", "enter_a"])


    def testExtraListener(self):
        self.called = []
        class Listener:
            post=""
            def enter_a(s): self.called.append("enter_a"+s.post)
            def exit_a(s): self.called.append("exit_a"+s.post)
            def enter_b(s): self.called.append("enter_b"+s.post)
            def exit_b(s): self.called.append("exit_b"+s.post)
        m = StateMachine(Listener())
        l2 = Listener()
        l2.post = "2"
        m.addListener(l2)
        m.set("a")
        self.assertEquals(self.called, ["enter_a", "enter_a2"])
        m.set("b")
        self.assertEquals(self.called, ["enter_a", "enter_a2", "exit_a2", "exit_a", "enter_b", "enter_b2"])



    def testExtraListenerWithArguments(self):
        self.called = []
	self.args = []
        class Listener:
            post=""
            def enter_a(s, *a): self.called.append("enter_a"+s.post); self.args += a
        m = StateMachine(Listener())
        l2 = Listener()
        l2.post = "2"
        m.addListener(l2, "foo", "bar", 1234)
        m.set("a")
        self.assertEquals(self.called, ["enter_a", "enter_a2"])
	self.assertEquals(self.args, ["foo", "bar", 1234])

