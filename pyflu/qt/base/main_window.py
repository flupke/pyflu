from os.path import basename
from PyQt4.QtGui import *
from PyQt4.QtCore import *    


class MainWindowBase(object):
    """
    A mixin class providing basic functionnality for QMainWindow.
    """

    state_setting = "state/main_window"
    geometry_setting = "state/main_window_geometry"

    def restore_state(self):
        settings = QSettings()
        self.restoreState(settings.value(self.state_setting,
            QVariant(True)).toByteArray())
        self.restoreGeometry(settings.value(self.geometry_setting,
            QVariant(True)).toByteArray())

    def save_state(self):
        settings = QSettings()
        settings.setValue(self.state_setting, QVariant(self.saveState()))
        settings.setValue(self.geometry_setting, QVariant(self.saveGeometry()))


class MdiMainWindow(MainWindowBase):
    """
    Mixin class for MDI style windows.
    """
    
    mdi_area_obj = "mdi_area"

    def closeEvent(self, event):
        mdi_area = getattr(self, self.mdi_area_obj)
        mdi_area.closeAllSubWindows()
        if len(mdi_area.subWindowList()):
            # Some scenes are still opened
            event.ignore()
        else:
            # don't show error reports past this point ...
            import sys
            sys.excepthook = lambda a, b, c: None
            # Save state and quit
            self.save_state()
            event.accept()            


class MruMainWindow(object):
    """
    A mixin class to handle MRU files lists.

    Subclasses must define the :attr:`mru_load_func` and :attr:`mru_menu` class
    attributes, which must be names of the load method (taking the file
    path as argument) and of the MRU menu item.
    """

    mru_setting = "state/most_recently_used_files"
    mru_length = 5
    mru_load_func = None
    mru_menu = None

    def mru_list(self):
        settings = QSettings()
        return list(settings.value(self.mru_setting,
                QVariant(QStringList())).toStringList())

    def set_mru_list(self, value):
        settings = QSettings()
        settings.setValue(self.mru_setting, QVariant(value))

    def add_to_mru(self, path):
        path = unicode(path)
        mru = self.mru_list()
        if path not in mru:
            # path not in mru yet, add it to the beginning
            mru.insert(0, path)
        else:
            # path is already in the mru, swap its position with the newest
            # entry
            path_index = mru.index(path)
            mru[0], mru[path_index] = mru[path_index], mru[0]
        # Prune oldest entries
        if len(mru) > self.mru_length:
            mru.pop(-1)
        self.set_mru_list(mru)
        self.refresh_mru_menu()

    def remove_from_mru(self, path):
        path = unicode(path)
        mru = self.mru_list()
        try:
            mru.remove(path)
        except ValueError:
            pass
        else:
            self.set_mru_list(mru)
        self.refresh_mru_menu()
        
    def mru_actions(self):
        ret = []
        for path in self.mru_list():
            action = QAction(basename(unicode(path)), self)
            action.setData(QVariant(path))
            self.connect(action, SIGNAL("triggered()"), self.open_mru)               
            ret.append(action)
        return ret

    def open_mru(self):
        action = self.sender()
        path = unicode(action.data().toString())
        getattr(self, self.mru_load_func)(path)

    def refresh_mru_menu(self):
        menu = getattr(self, self.mru_menu)
        menu.clear()
        menu.addActions(self.mru_actions())
