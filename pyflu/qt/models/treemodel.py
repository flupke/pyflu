from PyQt4.QtGui import *
from PyQt4.QtCore import *
from pyflu.qt.models.treenode import RenameError, FolderNode
try:
    import json
except ImportError:
    import simplejson as json


class TreeModel(QAbstractItemModel):
    """
    A base class for models using TreeNode based trees.

    Implementations must create a member variable named 'root_item' in their
    __init__ that conforms to the TreeNode interface.
    """

    num_columns = 1
    dnd_mime_type = "text/plain"

    # QAbstractItemModel interface

    def index(self, row, column, parent_index=QModelIndex()):
        if not self.hasIndex(row, column, parent_index):
            return QModelIndex()
        parent_item = self.item_from_index(parent_index)
        child_item = parent_item.children[row]
        return self.createIndex(row, column, child_item)

    def hasIndex(self, row, column, parent_index):
        if column < 0 or column >= self.num_columns or row < 0:
            return False
        parent_item = self.item_from_index(parent_index)
        if row >= len(parent_item.children):
            return False
        return True

    def parent(self, child_index):
        if not child_index.isValid():
            return QModelIndex()
        child_item = child_index.internalPointer()
        parent_item = child_item.parent
        if parent_item is None or parent_item is self.root_item:
            # Top level item
            return QModelIndex()
        # Get parent's row
        grand_parent = parent_item.parent
        row = grand_parent.child_index(parent_item)
        return self.createIndex(row, 0, parent_item)

    def rowCount(self, parent_index):
        if parent_index.column() >= self.num_columns:
            return 0
        parent_item = self.item_from_index(parent_index)
        return len(parent_item.children)

    def columnCount(self, parent_index):
        return self.num_columns

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        item = index.internalPointer()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return QVariant(item.name)
        elif role == Qt.DecorationRole:
            if item.icon is not None:
                return QVariant(item.icon)
        return QVariant()

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            item = index.internalPointer()
            try:
                item.rename(unicode(value.toString()))
            except RenameError, e:
                louie.send(signals.error, self, 
                    self.trUtf8("Can't rename item"), unicode(e))
                return False
            self.emit(SIGNAL("dataChanged()"))
            return True
        return False
    
    def flags(self, index):         
        item = self.item_from_index(index)
        flags = Qt.NoItemFlags
        if item.editable:
            flags |= Qt.ItemIsEditable
        if item.draggable:
            flags |= Qt.ItemIsDragEnabled
        if item.drop_target:
            flags |= Qt.ItemIsDropEnabled
        if item.selectable:
            flags |= Qt.ItemIsSelectable
        if item.enabled:
            flags |= Qt.ItemIsEnabled
        return flags

    def removeRow(self, row, parent_index=QModelIndex(), detach=True):
        """
        QAbstractItemModel.removeRow() implementation.

        Accepts an additional argument, ``detach`` that determines the action
        to take on the node pointed by the operation. If it is True (the
        default), the node's ``detach()`` method is called, if it is False the
        node's ``delete()`` method is called.
        """
        parent_item = self.item_from_index(parent_index)
        node = parent_item.children[row]
        self.beginRemoveRows(parent_index, row, row)
        if detach:
            node.detach()
        else:
            node.delete()
        self.endRemoveRows()
        return True

    def insertRow(self, node, row=None, parent_index=QModelIndex()):
        parent_item = self.item_from_index(parent_index)
        if row is None:
            row = len(parent_item.children)
        self.beginInsertRows(parent_index, row, row)
        parent_item.add_child(node)
        self.endInsertRows()
        return True

    # Drag and drop methods

    def supportedDropActions(self):
        return Qt.MoveAction    

    def mimeTypes(self):
        return [self.dnd_mime_type]

    def mimeData(self, indices):
        if not len(indices):
            return 0
        data = []
        for index in indices:
            if index.isValid():
                item = index.internalPointer()
                data.append(item.drag_data())
        mime_data = QMimeData()
        mime_data.setData(self.dnd_mime_type, self.dump_drag_data(data))
        return mime_data                
            
    # Utilities
    
    @classmethod
    def decode_mime(cls, mime_data):
        """
        Decode a QMimeData object coming from :meth:`mimeData` back to its 
        Python form.
        """
        return cls.load_drag_data(str(mime_data.retrieveData(cls.dnd_mime_type, 
                QVariant.String).toString()))

    @classmethod
    def dump_drag_data(cls, data):
        """
        Create a dump of ``data``, suitable to be inserted in a QMimeData.
        """
        return json.dumps(data)

    @classmethod
    def load_drag_data(cls, data):
        """
        Reverse dump_drag_data().
        """
        return json.loads(data)

    def item_from_index(self, index):
        if not index.isValid():
            return self.root_item
        return index.internalPointer()

    def delete(self, index):
        item = index.internalPointer()
        try:
            item.delete()
        except OSError, e:
            louie.send(signals.error, self, self.trUtf8("Can't delete item"),
                    self.trUtf8("Error deleting item: %1").arg(unicode(e[1])))
        else:
            self.beginRemoveRows(index.parent(), index.row(), index.row())
            self.endRemoveRows()

    def new_folder(self, index):
        item = index.internalPointer()
        # Insert the new folder just after the last folder
        insert_pos = 0
        for child in item.children:
            if not isinstance(child, FolderNode):
                break
            insert_pos += 1
        self.beginInsertRows(index, insert_pos, insert_pos)
        item.new_folder(insert_pos)
        self.endInsertRows()

