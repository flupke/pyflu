from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QTreeView, QAction, QMenu, QMessageBox
import louie


class TreeNodeView(QTreeView):
    """
    A QTreeView that supports TreeNode based models.
    """

    ctx_menu = {}
    """
    A name => text mapping context menu actions.

    TreeNodeView subclasses can define any context menu action, the method of
    the same name in the subclass will be used as the action's callback.
    """

    def __init__(self, parent=None):
        QTreeView.__init__(self, parent)
        # Connect
        self.connect(self, SIGNAL("customContextMenuRequested(QPoint)"),
                self.show_context_menu)
        self.connect(self, SIGNAL("doubleClicked(const QModelIndex&)"), 
                self.item_double_clicked)
        self.ctx_menu_actions = {}
        for name, text in self.ctx_menu.items():
            action = QAction(text, self)
            self.ctx_menu_actions[name] = action
            self.connect(action, SIGNAL("triggered()"), getattr(self, name))

    # Base class redefinitions

    def mouseReleaseEvent(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            self.clearSelection()
        return QTreeView.mouseReleaseEvent(self, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete()
        return QTreeView.keyReleaseEvent(self, event)

    # Other methods

    def show_context_menu(self, position):
        index = self.indexAt(position)
        if index.isValid():
            item = index.internalPointer()
            QMenu.exec_([self.ctx_menu_actions[a] for a in item.ctx_actions],
                    self.mapToGlobal(position))

    def item_double_clicked(self, index):
        pass

    def new_folder(self):
        index = self.currentIndex()
        self.model().new_folder(index)

    def rename(self):
        try:
            self.edit(self.currentIndex())
        except RenameError, e:
            QMessageBox.critical(self, self.trUtf8("Rename error"), unicode(e))

    def delete(self):
        """
        Delete the currently selected item.
        """
        index = self.currentIndex()
        if not index.isValid():
            return
        item = index.internalPointer()
        if not item.deletable:
            return
        if QMessageBox.question(self, self.trUtf8("Confirmation"), self.trUtf8(
            "Are you sure you want to delete this item ?")) == QMessageBox.Ok:
            self.model().delete(index)

    def model_error(self, title, text):
        QMessageBox.critical(self, title, text)

