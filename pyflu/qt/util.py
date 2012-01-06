from os.path import dirname, join
import warnings
import types
import functools
from PyQt4.QtGui import (QIcon, QPixmap, QCursor, QFileDialog, QApplication, 
        qRgb, qRgba, QDialog)
from PyQt4.QtCore import (Qt, QSettings, QVariant, PYQT_VERSION, QString,
        QCoreApplication)


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
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        try:
            res = func(*args, **kwargs)
        finally:
            QApplication.restoreOverrideCursor()
        return res
    return wrapper


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
        return
    save_path = unicode(dlg.selectedFiles()[0])
    # Remember save location directory
    settings.setValue(settings_path, QVariant(dirname(save_path)))
    return save_path


def get_open_path(parent, settings_path=None, filter=None,
        default_dir=None, default_filename=None, select_directory=False):
    """
    Shows an 'open file' dialog and returns the selected path.

    Also remembers the selected directory, so that subsequent calls to this
    function with the same *settings_path* will open in the last selected
    directory. The default directory can also be forced with *default_dir*.

    If *filter* is specified, it must be an iterable containing filters
    definitions. See the :func:`format_file_dialog_filter_string` docstring for
    details.

    If *default_filename* is given, select this file.

    If *select_directory* is ``True``, a directory is selected instead of a 
    file.

    Return None if the user canceled.
    """
    # Get the last used save directory
    settings = QSettings()
    if default_dir is None:
        if settings_path is not None:
            last_dir = unicode(settings.value(settings_path,
                QVariant(u"")).toString())
        else:
            last_dir = QString()
        default_dir = last_dir 
    # Get open location
    dlg = QFileDialog(parent)
    dlg.setWindowTitle(parent.trUtf8("Open"))
    if select_directory:
        dlg.setFileMode(QFileDialog.Directory)
    else:
        dlg.setFileMode(QFileDialog.ExistingFile)
    dlg.setAcceptMode(QFileDialog.AcceptOpen)
    dlg.setDirectory(default_dir)
    if default_filename is not None:
        dlg.selectFile(default_filename)
    if filter is not None:
        dlg.setNameFilter(format_file_dialog_filter_string(filter))
    if dlg.exec_() != QDialog.Accepted:
        return
    open_path = unicode(dlg.selectedFiles()[0])
    if settings_path is not None:
        # Remember opened location directory
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


def get_or_create_app(args=None, cls=QApplication):
    if args is None:
        args = []
    app = cls.instance()
    if app is None:
        app = cls(args)
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
