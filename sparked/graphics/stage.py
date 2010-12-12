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
import dbus

from twisted.internet import reactor

from sparked import events


class Stage (clutter.Stage):
    """
    Stage class.

    @ivar keys: Keymap with commonly used keys and their actions.
    @ivar debug: Whether debugging is enabled. This is retrieved from the --debug flag from the sparkd runner.
    """
    
    keys = {'fullscreen': gtk.keysyms.F11,
            'quit': (clutter.CONTROL_MASK, gtk.keysyms.q)}
    debug = False
    
    def __init__(self, app):
        clutter.Stage.__init__(self)
        self.app = app
        self.app.state.addListener(self)
        self.show()
        self.set_title(app.title + " - Stage")

        self.connect("destroy", lambda _: stageEvents.dispatch("stage-closed", self))
        self.connect("key-press-event", self.keyPress)

        self.debug = self.app.baseOpts['debug']
        self.addMonitors()

        # shutdown when stage is closed
        stageEvents.addObserver("stage-closed", lambda _: reactor.stop())
        # go fullscreen if not --debug
        if not self.debug:
            self.toggleFullscreen()

        self.created()


    def created(self):
        """
        Callback function when the construction of the stage is
        complete and it is ready to be shown at the screen.
        """


    def addMonitors(self):
        """
        Add a widget to the stage which shows when one of the monitors
        reports an error.
        """
        self.app.monitors.events.addObserver("updated", self.updateMonitors)
        self._monitorText = clutter.Text()
        self._monitorText.set_font_name("helvetica bold 18px")
        self._monitorText.set_color(clutter.color_from_string("#ff0000"))
        self._monitorText.set_x(3)
        self.add(self._monitorText)


    def updateMonitors(self, container):
        if container.ok():
            self._monitorText.hide()
            return
        txt = "ERROR: "
        for m in container.monitors:
            if not m.ok:
                txt += m.title+", "
        txt = txt[:-2]
        self._monitorText.set_text(txt)
        self._monitorText.show()
        self._monitorText.raise_top()


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

            self.screensaverInhibit("Fullscreen presentation")
        else:
            self.screensaverUnInhibit()


    screensaverInhibited = None
    """ Flag which is non-zero when the screensaver has been inhibited. """


    def screensaverInhibit(self, reason):
        """
        Prevent the screen saver from starting.
        """
        bus = dbus.SessionBus()
        iface = dbus.Interface(bus.get_object('org.gnome.ScreenSaver', "/org/gnome/ScreenSaver"), 'org.gnome.ScreenSaver')
        self.screensaverInhibited = iface.Inhibit(self.name, reason)


    def screensaverUnInhibit(self):
        """
        Resume the screen saver.
        """
        if not self.screensaverInhibited:
            return
        bus = dbus.SessionBus()
        iface = dbus.Interface(bus.get_object('org.gnome.ScreenSaver', "/org/gnome/ScreenSaver"), 'org.gnome.ScreenSaver')
        iface.UnInhibit(self.screensaverInhibited)
        self.screensaverInhibited = None



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
