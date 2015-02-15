from vanilla import Window, Tabs
from defconAppKit.windows.baseWindow import BaseWindowController


class BaseWindow(BaseWindowController):
    window_size = (500, 300)

    def __init__(self, active="Install"):
        self.first_tab = active
        self.w = Window(self.window_size,
                        autosaveName=self.__class__.__name__,
                        title=self.window_title)

    def open(self):
        if self.toolbar.items:
            self.create_toolbar()
            self.add_tabs()
            self.set_active_tab(self.first_tab)
        self.w.open()

    def create_toolbar(self):
        self.w.addToolbar(toolbarIdentifier="mechanicToolbar",
                          toolbarItems=self.toolbar.items,
                          addStandardItems=False)

    def set_active_tab(self, pane):
        current_index = self.w.tabs.get()
        index = self.toolbar.index_of(pane)
        if not self.w.isVisible():
            self.w.getNSWindow().toolbar().setSelectedItemIdentifier_(pane)
        self.w.tabs.set(index)
        self.w.tabs[current_index].view.deactivate()
        self.set_window_size(self.w.tabs[index].view)
        self.w.tabs[index].view.activate()

    def toolbar_select(self, sender):
        self.set_active_tab(sender.itemIdentifier())

    def add_tabs(self):
        self.w.tabs = Tabs((0, 0, -0, -0), self.toolbar.labels, showTabs=False)

        for index, item in enumerate(self.toolbar.items):
            tab = self.w.tabs[index]
            tab.view = item['view']((0, 0, -0, -0), self)

    def set_window_size(self, tab):
        self.w.resize(tab.tab_size[0], tab.tab_size[1], False)

    @property
    def current_tab(self):
        index = self.w.tabs.get()
        return self.w.tabs[index]

    @property
    def toolbar(self):
        try:
            return self.__toolbar
        except AttributeError:
            self.__toolbar = Toolbar(self)
            return self.__toolbar


class Toolbar(object):

    def __init__(self, window):
        self.items = []
        self.window = window

    def index_of(self, identifier):
        return next((index for index, item
                           in enumerate(self.items)
                           if item['itemIdentifier'] == identifier), 0)

    def add_item(self, view):
        item = dict(itemIdentifier=view.identifier,
                    label=view.title,
                    callback=self.window.toolbar_select,
                    imageNamed=view.image,
                    selectable=True,
                    view=view)
        self.items.append(item)

    @property
    def labels(self):
        return [item['label'] for item in self.items]