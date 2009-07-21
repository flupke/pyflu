from os.path import dirname, join
from PyQt4.QtGui import QIcon, QPixmap, QCursor, QFileDialog, QApplication
from PyQt4.QtCore import Qt, QSettings, QVariant


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
        res = func(*args, **kwargs)
        QApplication.restoreOverrideCursor()
        return res
    return f


def get_save_path(parent, settings_path, default_filename):
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
    save_path = QFileDialog.getSaveFileName(parent, 
            parent.trUtf8("Save as"), 
            join(last_dir, default_filename))
    if save_path.isNull():
        return None
    save_path = unicode(save_path)
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
