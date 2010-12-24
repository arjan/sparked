# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Interfaces to Mediamatic's network-based services.
"""

from twisted.internet import task
from twisted.python import log

from anymeta.api import AnyMetaAPI

from sparked import monitors


class AnymetaAPIMonitor (monitors.Monitor):
    """
    A L{sparked.monitors.Monitor} subclass which implements an 'api'
    attribute which holds a connection to an anyMeta website through
    the python-anymeta library.
    """

    title = "Anymeta API"

    checkInterval = 20
    app = None
    attribute = None

    looper = None


    def __init__(self, app, attribute='api'):
        self.app = app
        self.attribute = attribute
        self.app.events.addObserver("options-loaded", self.setAPI)


    def setAPI(self, opts):
        self.title = 'anyMeta API'
        if self.attribute not in opts:
            raise ValueError("Missing '%s' key in application options" % self.attribute)
        if not opts[self.attribute]:
            if self.looper:
                self.looper.stop()
                self.looper = None
            setattr(self.app, self.attribute, None)
            self.ok = None
            self.api = None
            self.container.update()
            return

        try:
            self.api = AnyMetaAPI.from_registry(opts[self.attribute], engine='twisted')
        except Exception:
            log.err()
            if self.looper:
                self.looper.stop()
                self.looper = None
            self.ok = False
            self.container.update()
            return

        self.title += " [%s]" % opts[self.attribute]
        setattr(self.app, self.attribute, self.api)
        if self.looper:
            self.looper.stop()
            self.looper = None
        self.looper = task.LoopingCall(self._check)
        self.looper.start(self.checkInterval)


    def _check(self):
        d = self.api.anymeta.user.info()
        def ok(_):
            if not self.ok:
                self.app.events.dispatch('anymeta-api-connected', self.attribute)
            self.ok = True
        def err(f):
            if self.ok:
                self.app.events.dispatch('anymeta-api-disconnected', self.attribute)
            self.ok = False
            log.err(f)
        d.addCallbacks(ok, err)
        d.addCallback(lambda _: self.container.update())
        return d


class MediamaticWebMonitor(monitors.NetworkWebMonitor):
    title = "hwdeps.mediamatic.nl"

    def __init__(self):
        from socket import gethostname
        monitors.NetworkWebMonitor.__init__(self, "http://hwdeps.mediamatic.nl/ping.php?host="+gethostname())
