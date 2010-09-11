# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
A grapihical window implemented using the
U{clutter<http://www.clutter-project.org/>} library, for interactive
displays.

F11 toggles fullscreen.
"""

import gtk
import clutter

from twisted.internet import reactor

from sparked import events


class Stage (clutter.Stage):

    keys = {'fullscreen': gtk.keysyms.F11,
            'quit': (clutter.CONTROL_MASK, gtk.keysyms.q)}

    def __init__(self, app):
        clutter.Stage.__init__(self)
        self.app = app
        self.app.state.addListener(self)
        self.show()
        self.set_title(app.title + " - Graphics")

        self.connect("destroy", lambda _: stageEvents.dispatch("stage-closed", self))
        self.connect("key-press-event", self.keyPress)

        self.debug = self.app.baseOpts['debug']
        self.created()


    def created(self):
        """
        Callback function when the construction of the stage is
        complete and it is ready to be shown at the screen.
        """


    def keyPress(self, actor, event):
        """
        Handle keypresses.
        """
        if self.isKey(event, self.keys['fullscreen']):
            self.toggleFullscreen()
        if self.isKey(event, self.keys['quit']):
            reactor.stop()


    def isKey(self, event, keydef):
        if type(keydef) != tuple:
            return event.keyval == keydef

        for m in keydef[:-1]:
            if not (event.modifier_state & m):
                return False
        return event.keyval == keydef[-1]



    def toggleFullscreen(self):
        """
        Toggle this stage fullscreen or not.
        """
        self.set_fullscreen(not self.get_fullscreen())
        stageEvents.dispatch("stage-fullscreentoggled", stage=self)
        self.show_cursor()

        if not self.get_fullscreen():
            # we're fullscreen here
            if not self.debug:
                self.hide_cursor()

            self.app.screensaverInhibit("Fullscreen presentation")
        else:
            self.app.screensaverUnInhibit()


def positionInBox(actor, box):
    """
    Given an actor and a box (also an actor), position the actor
    inside the box, adjusting its position and size, while preserving
    the aspect ratio of the actor.
    """
    aw, ah = actor.get_width(), actor.get_height()
    bw, bh = box.get_width(), box.get_height()

    aspect = ah/float(aw)

    if bw*aspect <= bh:
        actor.set_width(bw)
        actor.set_height(bw*aspect)
        actor.set_x(box.get_x())
        actor.set_y(box.get_y()+(bh-bw*aspect)*0.5)
    else:
        actor.set_height(bh)
        actor.set_width(bh/aspect)
        actor.set_y(box.get_y())
        actor.set_x(box.get_x()+(bw-bh/aspect)*0.5)


stageEvents = events.EventDispatcher()
