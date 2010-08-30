# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

"""
A status window for the Spark application.
"""

from datetime import datetime
import gtk

from twisted.python import log

from sparked import events

class StatusWindowClosed(events.Event):
    pass

class StatusWindow (gtk.Window):
    """
    The status window for the sparked application.
    Contains the log area
    """

    maxLogLines = 2000

    def __init__(self, app):
        gtk.Window.__init__(self)
        self.app = app
        self.set_title(app.title + " - Status window")
        self.connect("destroy", self.closed)

        self.build()
        log.addObserver(self.log)


    def build(self):
        """
        Create the status window
        """
        self.box = gtk.HBox()
        self.log_area = gtk.TextView()
        w = gtk.ScrolledWindow()
        w.add(self.log_area)

        self.box.pack_end(w, True, True, 0)

        if self.app.monitors:
            # Create the monitor widget and connect
            w = MonitorWidget(self.app.monitors)
            self.box.pack_start(w, False, False, 0)

        self.add(self.box)
        self.set_size_request(720, 300)
        self.show_all()


    def closed(self, window):
        log.removeObserver(self.log)
        guiEvents.sendEvent(StatusWindowClosed(window=window))


    def log(self, dict):
        """
        Log observer that writes into the log scroller area of the UI.

        This method implements C{twisted.python.log.ILogObserver}.
        """
        b = self.log_area.get_buffer()

        end = b.get_end_iter()
        b.place_cursor(end)

        for m in dict['message']:
            b.insert_at_cursor("%s | %s\n" % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), m))

        if b.get_line_count() > self.maxLogLines:
            frm = b.get_start_iter()
            to  = b.get_iter_at_line(b.get_line_count() - self._max_log_lines)
            b.delete(frm, to)
        self.log_area.scroll_to_iter(b.get_end_iter(), 0.0)



class MonitorWidget(gtk.VBox):
    """
    A widget which is tied to a L{monitors.MonitorContainer} object;
    receiving updates as the monitors in the container change state.
    It shows a list with the titles  and the state of each monitor.
    """

    stock_map = { True: "gtk-apply",
                  False: "gtk-stop"
                  }


    def __init__(self, container):
        gtk.VBox.__init__(self)
        self.set_property("width_request", 240)
        container.events.addEventListener(self.refresh)


    def refresh(self, e):
        """
        Refresh the state when a L{monitors.MonitorEvent} comes in.
        """
        for c in self.get_children():
            self.remove(c)

        for c in e.container.monitors:
            v = gtk.HBox()
            l = gtk.Label(c.title)
            l.set_property("xalign", 0)
            v.pack_start(l, True, True, 10)

            im = gtk.Image()
            im.set_from_stock(self.stock_map[c.ok], gtk.ICON_SIZE_MENU)
            v.pack_start(im, False, True, 10)

            self.pack_start(v, False, False, 10)
            self.pack_start(gtk.HSeparator(), False, True, 0)

        self.show_all()


guiEvents = events.EventGroup()
