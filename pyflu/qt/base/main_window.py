from PyQt4.QtGui import *
from PyQt4.QtCore import *    


class MainWindow(object):
    """
    A mixin class providing basic functionnality for QMainWindow.
    """

    def restore_state(self):
        settings = QSettings()
        self.restoreState(settings.value("state/main_window",
            QVariant(True)).toByteArray())

    def save_state(self):
        settings = QSettings()
        settings.setValue("state/main_window", QVariant(self.saveState()))


class MdiMainWindow(MainWindow):
    """
    Mixin class for MDI style windows.
    """
    
    _mdi_area_obj = "mdi_area"

    def closeEvent(self, event):
        mdi_area = getattr(self, self._mdi_area_obj)
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

