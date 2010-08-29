# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

import gtk
import clutter

from blurb import events

class StageClosed(events.Event):
    pass

class StageFullscreenToggled(events.Event):
    pass


class Stage (clutter.Stage):

    def __init__(self, app):
        clutter.Stage.__init__(self)
        self.app = app
        self.app.state.addListener(self)
        self.show()
        self.set_title(app.title + " - Graphics")

        self.connect("destroy", lambda _: stageEvents.sendEvent(StageClosed(stage=self)))
        self.connect("key-press-event", self.keyPress)

        #print self.x11_get_window()


    def keyPress(self, actor, event):
        if event.keyval == gtk.keysyms.F11:
            self.toggleFullscreen()


    def toggleFullscreen(self):
        """
        Toggle this stage fullscreen or not.
        """
        self.set_fullscreen(not self.get_fullscreen())
        stageEvents.sendEvent(StageFullscreenToggled(stage=self))


stageEvents = events.EventGroup()
