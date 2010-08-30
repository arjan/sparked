# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.
# -*- test-case-name: sparked.test.test_events -*-

"""
Classes which define a generic event system.
"""

from twisted.words.xish import utility

class EventDispatcher(utility.EventDispatcher):
    """
    The sparked event dispatcher is simpler than the twisted version:
    it does not use XPath arguments and its event prefix is always
    empty.

    This class exists to simplify the implementation of event
    dispatchers in sparked without the syntactic sugar of xish'
    EventDispatcher class.
    """
    def __init__(self, eventprefix=""):
        utility.EventDispatcher.__init__(self, eventprefix)


    def dispatch(self, event, *arg, **kwarg):
        """
        Dispatch the named event to all the callbacks.
        """
        foundTarget = False

        self._dispatchDepth += 1

        observers = self._eventObservers

        priorities = observers.keys()
        priorities.sort()
        priorities.reverse()

        emptyLists = []
        for priority in priorities:
            for query, callbacklist in observers[priority].iteritems():
                if query == event:
                    callbacklist.callback(*arg, **kwarg)
                    foundTarget = True
                    if callbacklist.isEmpty():
                        emptyLists.append((priority, query))

        for priority, query in emptyLists:
            del observers[priority][query]

        self._dispatchDepth -= 1

        # If this is a dispatch within a dispatch, don't
        # do anything with the updateQueue -- it needs to
        # wait until we've back all the way out of the stack
        if self._dispatchDepth == 0:
            # Deal with pending update operations
            for f in self._updateQueue:
                f()
            self._updateQueue = []

        return foundTarget
