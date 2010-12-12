# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Tests for sparked.launcher.*

Maintainer: Arjan Scherpenisse
"""
from twisted.python import usage
from twisted.trial import unittest

from sparked import launcher

class TestLauncher(unittest.TestCase):
    """
    Test the L{sparked.launcher}
    """

    def testLaunchMissingApplicationName(self):
        self.assertRaises(usage.UsageError, launcher.launchApplication, [])

    def testLaunchApplicationNotFound(self):
        self.assertRaises(usage.UsageError, launcher.launchApplication, ["somethingthatdoesnotexist"])
