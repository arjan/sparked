# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Simple bidirectional asynchronous message passing between a web page
and a Sparked application. Uses comet long-polling as communication
mechanism.
"""

import os
import simplejson as json

from twisted.web import resource, static, server, http
from sparked import events


class IOClient(object):
    """
    Represents a single client connection.

    @ivar request: The current L{twisted.web.http.Request} comet connection

    @ivar queue: Intenral message queue when sending messages before
    the comet connection has been re-established.
    """

    request = None
    queue = None

    def __init__(self, request):
        self.request = request
        self.events = events.EventDispatcher()
        self.queue = []


    def send(self, message):
        if not self.request:
            self.queue.append(message)
            return
        self.request.write(json.dumps(message))
        self.request.finish()
        self.request = None # rely on javascript to open a new comet request


    def setRequest(self, request):
        self.request = request
        if self.queue:
            self.send(self.queue[0])
            del self.queue[0]



CLIENT_HEADER = "X-IO-ClientID"

def lookupClientId(request):
    """
    Given a L{twisted.web.http.Request}, lookup the client id. Aborts
    the request if no client id is found.
    """
    if not request.requestHeaders.hasHeader(CLIENT_HEADER):
        request.setResponseCode(http.NOT_ACCEPTABLE)
        request.write("Not acceptable\n")
        request.finish()
        return None
    return request.requestHeaders.getRawHeaders(CLIENT_HEADER)[0]



class Receiver(resource.Resource):
    """
    The endpoint for the comet long-poll. The request's connection is
    kept open and registered in the clients table.
    """
    def __init__(self, io):
        resource.Resource.__init__(self)
        self.io = io

    def render_POST(self, request):
        clientId = lookupClientId(request)
        if not clientId:
            return
        def rm(_):
            self.io.removeClient(clientId)
        request.notifyFinish().addErrback(rm)
        self.io.addClient(clientId, request)
        return server.NOT_DONE_YET



class Sender(resource.Resource):
    """
    The endpoint for incoming messages
    """

    def __init__(self, io):
        resource.Resource.__init__(self)
        self.io = io

    def render_POST(self, request):
        clientId = lookupClientId(request)
        if not clientId:
            return
        message = json.loads(request.content.read())
        self.io.clients[clientId].events.dispatch("message", message)
        request.finish()



class IOResource(resource.Resource):
    """
    Main entrypoint which manages the currently connected clients. Has
    send/receive childs for handling incoming and outgoing messages,
    as well as serve the JavaScript client library.
    """

    clients = None
    events = None

    def __init__(self):
        resource.Resource.__init__(self)
        self.clients = {}
        self.putChild("lib.js", static.File(os.path.join(os.path.dirname(__file__), "io.js"), defaultType="text/javascript"))
        self.putChild("recv", Receiver(self))
        self.putChild("send", Sender(self))
        self.events = events.EventDispatcher()


    def addClient(self, clientId, request):
        if clientId in self.clients:
            # just update the current poll request
            self.clients[clientId].setRequest(request)
            return
        client = IOClient(request)
        self.clients[clientId] = client
        self.events.dispatch("connection", client)


    def removeClient(self, clientId):
        self.clients[clientId].events.dispatch("disconnect")
        del self.clients[clientId]



def listen(site, prefix="sparked.web.io"):
    """
    Serve a sparked.web.io endpoint at the given prefix.

    @param site: the L{twisted.web.server.Site} instance at which to serve
    @return: An L{IOResource}
    """
    res = IOResource()
    site.resource.putChild(prefix, res)
    return res
