# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
Simple bidirectional asynchronous message passing between web and sparked app
"""

import os

from twisted.web import resource, static, server, http

from sparked import events



class IOClient(object):

    request = None

    def __init__(self, request):
        self.request = request
        self.events = events.EventDispatcher()

    def send(self, message):
        print ">>> SEND", message, self.request
        self.request.write(message)
        self.request.finish()
        #self.request = None # rely on javascript to open a new comet request


CLIENT_HEADER = "X-IO-ClientID"

def lookupClientId(request):
    if not request.requestHeaders.hasHeader(CLIENT_HEADER):
        request.setResponseCode(http.NOT_ACCEPTABLE)
        request.write("Not acceptable\n")
        request.finish()
        return None
    return request.requestHeaders.getRawHeaders(CLIENT_HEADER)[0]



class Receiver(resource.Resource):

    def __init__(self, io):
        resource.Resource.__init__(self)
        self.io = io

    def render_POST(self, request):
        clientId = lookupClientId(request)
        if not clientId:
            return
        def rm(_):
            print "bye"
            self.io.removeClient(clientId)
        request.notifyFinish().addErrback(rm)
        self.io.addClient(clientId, request)
        return server.NOT_DONE_YET



class Sender(resource.Resource):

    def __init__(self, io):
        resource.Resource.__init__(self)
        self.io = io

    def render_POST(self, request):
        clientId = lookupClientId(request)
        if not clientId:
            return
        message = request.content.read()
        self.io.clients[clientId].events.dispatch("message", message)
        request.finish()



class IOResource(resource.Resource):

    clients = None
    events = None

    def __init__(self):
        resource.Resource.__init__(self)
        self.clients = {}
        self.putChild("lib.js", static.File(os.path.join(os.path.dirname(__file__), "_io_lib.js"), defaultType="text/javascript"))
        self.putChild("recv", Receiver(self))
        self.putChild("send", Sender(self))
        self.events = events.EventDispatcher()


    def addClient(self, clientId, request):
        if clientId in self.clients:
            # just update the current poll request
            self.clients[clientId].request = request
            return
        client = IOClient(request)
        self.clients[clientId] = client
        self.events.dispatch("connection", client)


    def removeClient(self, clientId):
        self.clients[clientId].events.dispatch("disconnect")
        del self.clients[clientId]




def listen(site):
    res = IOResource()
    site.resource.putChild("sparked.web.io", res)
    return res
