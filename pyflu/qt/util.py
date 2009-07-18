from PyQt4.QtGui import QIcon, QPixmap


def icon_from_res(path):
    """Create an icon from a resource path"""
    icon = QIcon()
    icon.addPixmap(QPixmap(path), QIcon.Normal, QIcon.Off)
    return icon
