# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Tests for sparked.application.*

Maintainer: Arjan Scherpenisse
"""

from twisted.trial import unittest

from sparked.application import getPath

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

