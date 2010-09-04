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

from sparked import events


class Stage (clutter.Stage):

    keys = {'fullscreen': gtk.keysyms.F11}

    def __init__(self, app):
        clutter.Stage.__init__(self)
        self.app = app
        self.app.state.addListener(self)
        self.show()
        self.set_title(app.title + " - Graphics")

        self.connect("destroy", lambda _: stageEvents.dispatch("stage-closed", self))
        self.connect("key-press-event", self.keyPress)

        self.debug = self.app.baseOpts['debug']


    def keyPress(self, actor, event):
        if event.keyval == self.keys['fullscreen']:
            self.toggleFullscreen()


    def toggleFullscreen(self):
        """
        Toggle this stage fullscreen or not.
        """
        self.set_fullscreen(not self.get_fullscreen())
        stageEvents.dispatch("stage-fullscreentoggled", stage=self)
        self.show_cursor()
        if not self.debug and not self.get_fullscreen():
            self.hide_cursor()


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
