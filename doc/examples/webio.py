# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Demonstrating sparked.web.io
"""
import os

from twisted.web import static, resource, server
from twisted.internet import reactor

from sparked import application
from sparked.web.io import listen


class Application(application.Application):

    title = "sparked.web.io example"

    def starting(self):
        root = resource.Resource()
        root.putChild("", static.File(os.path.join(os.path.dirname(__file__), "webio.html")))
        site = server.Site(root)
        io = listen(site)
        reactor.listenTCP(8880, site)

        io.events.addObserver("connection", self.newClient)


    def newClient(self, c):
        print "new client", c
        c.send({'message': 'hello'})

        def p(msg):
            print "client message:", msg
            c.send({'pong': msg})
        c.events.addObserver("message", p)
