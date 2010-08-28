# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

from twisted.application import service

from blurb import events


class Blurb(service.MultiService):
    """
    The blurb base class.

    All blurb plugins inherit from this class.
    """


    def __init__(self, opts, pluginOpts):
        service.MultiService.__init__(self)
        
        self.opts = opts
        self.pluginOpts = pluginOpts


systemEvents = events.EventGroup()
