# Copyright (c) 2011 Arjan Scherpenisse
# See LICENSE for details.

"""
Utility functions for simplified use of L{twisted.web}.
"""

from twisted.web import http, resource, static

import os
import tempfile
from email.Parser import Parser


class UploadResource(resource.Resource):
    """
    A simple resource for uploading a file to.

    On success, callback will be called with arguments (request, tempfilename, opts)
    opts contains 'filename' (real uploaded file name), 'referer' and 'mime'.

    On error, errback will be called with arguments (request, referer).
    """

    def __init__(self, callback, errback):
        self.callback = callback
        self.errback = errback


    def render_POST(self, request):
        referer = "/"
        body = ""
        for k, vs in request.requestHeaders.getAllRawHeaders():
            for v in vs:
                if k.lower() == "referer":
                    referer = v
                body += k + ": " + v + "\r\n"
        body += "\r\n"
        body += "".join(request.content.readlines())

        p = Parser()
        msg = p.parsestr(body)
        foundPart = None
        for part in msg.walk():
            if part.is_multipart():
                continue
            if part.get_filename():
                foundPart = part
                break

        if not foundPart:
            return self.errback(request, referer)

        payload = foundPart.get_payload()
        fp, fn = tempfile.mkstemp()
        os.write(fp, payload)
        os.close(fp)

        opts = {'filename': foundPart.get_filename(),
                'mime': foundPart.get_content_type(),
                'referer': referer}
        return self.callback(request, fn, opts)



def wrapBasicAuthentication(res, user, pw, realm="Please log in."):
    """
    Wraps a simple single user+password HTTP authentication around the
    given resource and all its children.
    """
    if hasattr(res.render, '_wrapped'):
        return res
    origRender = res.render
    def render(request):
        request.setHeader('WWW-Authenticate', 'Basic realm="%s"' % realm)
        if request.getUser() != user or request.getPassword() != pw:
            request.setResponseCode(http.UNAUTHORIZED)
            request.setHeader('WWW-Authenticate', 'Basic realm="%s"' % realm)
            return static.Data("<body><h1>Unauthorized</h1><p>Cannot access %s</p></body>\n" % realm, "text/html").render(request)
        return origRender(request)
    res.render = render
    res.render._wrapped = True

    origGetChildWithDefault = res.getChildWithDefault
    def getChildWithDefault(name, request):
        return wrapBasicAuthentication(origGetChildWithDefault(name, request), user, pw, realm)
    res.getChildWithDefault = getChildWithDefault
    return res
