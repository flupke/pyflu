from PyQt4.QtCore import Qt, QVariant
from pyflu.qt.models.treemodel import TreeModel


class TableModel(TreeModel):

    header = None
    """
    This should be a sequence containing horizontal header labels.
    """

    def data(self, index, role=Qt.DisplayRole):
        column = index.column()
        if not index.isValid():
            return QVariant()
        item = index.internalPointer()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if column == 0:
                return QVariant(item.name)
            else:
                try:
                    return QVariant(item.sub_names[column - 1])
                except IndexError:
                    pass
        elif role == Qt.DecorationRole:
            if column == 0:
                if item.icon is not None:
                    return QVariant(item.icon)
            else:
                try:
                    icon = item.sub_icons[column - 1]
                except IndexError:
                    pass
        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                if self.header:
                    return self.header[section]
        return QVariant()
