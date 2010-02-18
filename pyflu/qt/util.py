from os.path import dirname, join
from PyQt4.QtGui import QIcon, QPixmap, QCursor, QFileDialog, QApplication, \
        qRgb, qRgba, QDialog
from PyQt4.QtCore import Qt, QSettings, QVariant, PYQT_VERSION, QString
import warnings
import types


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
        default_suffix=None, filter=None):
    """
    Shows a 'save' dialog and returns the selected path.

    Also remembers the selected folder, so that subsequent calls to this
    function with the same ``settings_path`` will open in the last selected
    directory.

    If ``filter`` is specified, it must be an iterable containing filters
    definitions. See the ``format_file_dialog_filter_string()`` docstring for
    details.

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
    if filter is not None:
        dlg.setNameFilter(format_file_dialog_filter_string(filter))
    if dlg.exec_() != QDialog.Accepted:
        return None
    save_path = unicode(dlg.selectedFiles()[0])
    # Remember save location directory
    settings.setValue(settings_path, QVariant(dirname(save_path)))
    return save_path


def get_open_path(parent, settings_path, filter=None):
    """
    Shows an 'open file' dialog and returns the selected path.

    Also remembers the selected folder, so that subsequent calls to this
    function with the same ``settings_path`` will open in the last selected
    directory.

    If ``filter`` is specified, it must be an iterable containing filters
    definitions. See the ``format_file_dialog_filter_string()`` docstring for
    details.

    Returns None if the user canceled.
    """
    # Get the last used save directory
    settings = QSettings()
    last_dir = unicode(settings.value(settings_path, QVariant(u"")).toString())
    # Get save location
    if filter is not None:
        filter = format_file_dialog_filter_string(filter)
    else:
        filter = QString()
    open_path = QFileDialog.getOpenFileName(parent, parent.trUtf8("Open"), 
            last_dir, filter)
    if open_path.isNull():
        return None
    open_path = unicode(open_path)
    # Remember save location directory
    settings.setValue(settings_path, QVariant(dirname(open_path)))
    return open_path


def rgba(r, g, b, a=255):
    if PYQT_VERSION <= 263172:
        return (qRgba(r, g, b, a) & 0xffffff) - 0x1000000
    return qRgba(r, g, b, a)


def rgb(r, g, b):
    if PYQT_VERSION <= 263172:
        return (qRgb(r, g, b) & 0xffffff) - 0x1000000
    return qRgb(r, g, b)


def unpack_rgba(value):
    alpha = (value & 0xff000000) >> 24
    red = (value & 0xff0000) >> 16
    green = (value & 0xff00) >> 8
    blue = value & 0xff
    return red, green, blue, alpha


def get_or_create_app(args=None):
    if args is None:
        args = []
    app = QApplication.instance()
    if app is None:
        app = QApplication(args)
    return app
    

def format_file_dialog_filter_string(defs):
    """
    Make a filter string for QFileDialog objects from a list of definitions.

    Each element of ``defs`` is a pair, containing the filter name, and a list
    of extensions. The extensions must be strings, specified in wildcard format
    (e.g. '*.jpg', '*.svg', etc...). A single string can be used if there is
    only one extension specified.
    """
    parts = []
    for name, exts in defs:
        if isinstance(exts, types.StringTypes):
            exts = [exts]
        parts.append("%s (%s)" % (name, " ".join(exts)))
    return ";;".join(parts)
