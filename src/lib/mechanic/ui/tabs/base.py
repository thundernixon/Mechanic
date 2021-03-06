from AppKit import NSView
from vanilla import VanillaBaseObject, Sheet, TextBox, Button, Group

from mechanic.ui.text import Text
from mechanic.ui.overlay import Overlay


class BaseTab(VanillaBaseObject):
    ns_view_class = NSView
    tab_size = (500, 300)

    def __init__(self, dimensions, parent=None):
        self._setupView(self.ns_view_class, dimensions)
        self.parent = parent
        self.setup()

    def setup(self):
        pass

    def activate(self):
        pass

    def deactivate(self):
        pass

    def disable(self, text=''):
        if hasattr(self, 'overlay'):
            del self.overlay
        self.overlay = Overlay(text)

    def enable(self):
        if hasattr(self, 'overlay'):
            del self.overlay

    def start_progress(self, *args, **kwargs):
        return self.parent.start_progress(*args, **kwargs)

    def close_notification_sheet(self, sender):
        self.w.notification.close()

    def show_notification_sheet(self, text, size=(300, 80)):
        self.w.notification = Sheet(size, self.parent.w)
        self.w.notification.text = TextBox((15, 15, -50, -15), text)
        self.w.notification.closeButton = Button((-115, -37, 100, 22),
                                                 'Close',
                                                 callback=self.close_notification_sheet)
        self.w.notification.setDefaultButton(self.parent.w.notification.closeButton)
        self.w.notification.open()

    def show_connection_error_sheet(self):
        self.show_notification_sheet("Couldn't connect to the Internet...")

    def set_default_button(self, button):
        self.w.setDefaultButton(button)

    @property
    def w(self):
        return self.parent.w

    @property
    def max_tab_size(self):
        return self.tab_size
