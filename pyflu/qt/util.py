from os.path import dirname, join
from PyQt4.QtGui import QIcon, QPixmap, QCursor, QFileDialog, QApplication, \
        qRgb, qRgba, QDialog
from PyQt4.QtCore import Qt, QSettings, QVariant, PYQT_VERSION
import warnings


def icon_from_res(path):
    """Create an icon from a resource path"""
    icon = QIcon()
    icon.addPixmap(QPixmap(path), QIcon.Normal, QIcon.Off)
    return icon


def long_operation(func):
    """
    Decorator that changes the application cursor during the execution of a
    function.
    """
    def f(*args, **kwargs):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        try:
            res = func(*args, **kwargs)
        finally:
            QApplication.restoreOverrideCursor()
        return res
    return f


def get_save_path(parent, settings_path, default_filename=None, 
        default_suffix=None):
    """
    Shows a 'save' dialog and returns the selected path.

    Also remembers the selected folder, so that subsequent calls to this
    function with the same ``settings_path`` will open in the last selected
    directory.

    Returns None if the user canceled.
    """
    # Get the last used save directory
    settings = QSettings()
    last_dir = unicode(settings.value(settings_path, QVariant(u"")).toString())
    # Get save location
    dlg = QFileDialog(parent)
    dlg.setWindowTitle(parent.trUtf8("Save as"))
    dlg.setFileMode(QFileDialog.AnyFile)
    dlg.setAcceptMode(QFileDialog.AcceptSave)
    dlg.setDirectory(last_dir)
    if default_suffix is not None:
        dlg.setDefaultSuffix(default_suffix)
    if default_filename is not None:
        dlg.selectFile(default_filename)
    if dlg.exec_() != QDialog.Accepted:
        return None
    save_path = unicode(dlg.selectedFiles()[0])
    # Remember save location directory
    settings.setValue(settings_path, QVariant(dirname(save_path)))
    return save_path


def get_open_path(parent, settings_path):
    """
    Shows an 'open file' dialog and returns the selected path.

    Also remembers the selected folder, so that subsequent calls to this
    function with the same ``settings_path`` will open in the last selected
    directory.

    Returns None if the user canceled.
    """
    # Get the last used save directory
    settings = QSettings()
    last_dir = unicode(settings.value(settings_path, QVariant(u"")).toString())
    # Get save location
    open_path = QFileDialog.getOpenFileName(parent, parent.trUtf8("Open"), 
            last_dir)
    if open_path.isNull():
        return None
    open_path = unicode(open_path)
    # Remember save location directory
    settings.setValue(settings_path, QVariant(dirname(open_path)))
    return open_path


def rgba(r, g, b, a=255):
    if PYQT_VERSION <= 263172:
        warnings.warn("using untested qRgba fix")
        return (qRgba(r, g, b, a) & 0xffffff) - 0x1000000
    return qRgba(r, g, b, a)


def rgb(r, g, b):
    if PYQT_VERSION <= 263172:
        return (qRgb(r, g, b) & 0xffffff) - 0x1000000
    return qRgb(r, g, b)


def get_or_create_app(args=None):
    if args is None:
        args = []
    app = QApplication.instance()
    if app is None:
        app = QApplication(args)
    return app
    
