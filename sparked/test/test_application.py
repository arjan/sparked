# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Tests for sparked.application.*

Maintainer: Arjan Scherpenisse
"""
import tempfile

from twisted.trial import unittest

from sparked.application import getPath, Options

class TestGetPath(unittest.TestCase):
    """
    Test the L{application.getPath}
    """

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
        import os
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

