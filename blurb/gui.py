# Copyright (c) 2010 Arjan Scherpenisse
# See LICENSE for details.

from datetime import datetime
import gtk

from twisted.python import log

from blurb import events

class StatusWindowClosed(events.Event):
    pass

class StatusWindow (gtk.Window):
    """
    The status window for the blurb application.
    Contains the log area
    """

    maxLogLines = 2000

    def __init__(self, app):
        gtk.Window.__init__(self)
        self.app = app
        self.set_title(app.title + " - Status window")
        self.connect("destroy", self.closed)

        self.log_area = gtk.TextView()
        w = gtk.ScrolledWindow()
        w.add(self.log_area)
        self.add(w)
        self.set_size_request(500, 300)
        self.show_all()
        log.addObserver(self.log)


    def closed(self, window):
        guiEvents.sendEvent(StatusWindowClosed(window=window))


    def log(self, dict):
        """
        Log observer that writes into the log scroller area of the UI.

        This method implements L{log.ILogObserver}.
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


guiEvents = events.EventGroup()
