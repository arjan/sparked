#!/usr/bin/env python
# -*- test-case-name: blurb.test.test_events -*-
# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.


class Event(object):
    """
    a generic event class.
    """
    def __init__(self, **kw):
        self.__dict__.update(kw)


    def __eq__(self, e):
        return self.__dict__ == e.__dict__


    def __repr__(self):
        return u"[Event: %s]" % str(self.__dict__)



class EventGroup(object):
    """
    An event group defines a confined scope of event listeners.
    """

    def __init__(self):
        self.listeners = []


    def receiveEvents(self, *matches):
        """
        Decorator object for receiving events.
        """
        def wrap(f):
            if not len(matches):
                self.listeners.append( (f, True) )
            else:
                self.listeners.append( (f, matches) )
            return f

        return wrap


    def sendEvent(self, e):
        """
        Send event to my listeners.
        """
        [f(e) for f, match in self.listeners if self.eventMatches(e, match)]


    def eventMatches(self, event, match):
        if match == True:
            return True
        for cls in match:
            if isinstance(event, cls):
                return True
        return False
