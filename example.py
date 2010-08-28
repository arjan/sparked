# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.
#
# Example runner class for blurb.

from twisted.python import usage
from blurb import base

class Options(usage.Options):
    optFlags = [["fast", "f", "Run fast"]]


class Blurb(base.Blurb):

    def enter_start(self):
        self.state.setAfter("ping", 10)

    def enter_ping(self):
        self.state.setAfter("start", 10)

