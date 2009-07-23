import os
from pyflu.translation import ugettext as _
from pyflu.qt.util import icon_from_res
import shutil


class NodeOperationError(Exception): pass
class RenameError(NodeOperationError): pass


class TreeNode(object):
    """
    Base implementation for TreeNode objects.
    """

    icon = None
    ctx_actions = ()
    editor = None
    editable = False
    deletable = False

    def __init__(self, name=None, parent=None):
        self.children = []
        self.name = name
        self.parent = parent

    def is_leaf(self):
        return not bool(self.children)

    def add_child(self, child, insert_pos=None):
        if insert_pos is not None:
            self.children.insert(insert_pos, child)
        else:
            self.children.append(child)
        child.parent = self

    def child_index(self, child):
        return self.children.index(child)

    def rename(self, new_name):
        self.name = new_name

    def delete(self):
        self.parent.children.remove(self)


class FileSystemItemNode(TreeNode):
    """
    File system item (folders and files) node.
    """

    editable = True
    deletable = True

    def rename(self, new_name):
        parent_dir = os.path.dirname(self.path)
        new_path = os.path.join(parent_dir, new_name)
        if os.path.exists(new_path):
            raise RenameError(_("An item of this name already exists"))
        shutil.move(self.path, new_path)
        self.path = new_path
        super(FileSystemItemNode, self).rename(new_name)


class FolderNodeMixin(object):

    def new_folder(self, insert_pos=None):
        """
        Create a new child folder with a default name.
        """
        name = _("New folder")
        i = 0
        n = name
        while os.path.exists(os.path.join(self.path, n)):
            n = "%s %d" % (name, i)
            i += 1
        name = n
        new_path = os.path.join(self.path, name)
        os.mkdir(new_path)
        if hasattr(self, "folder_class"):
            cls = self.folder_class
        else:
            cls = self.__class__
        self.add_child(cls(new_path, name), insert_pos)


class FolderNode(FileSystemItemNode, FolderNodeMixin):
    
    ctx_actions = ("rename", "new_folder")
    icon = icon_from_res(":/images/folder.png")

    def __init__(self, path, name, parent=None):
        super(FolderNode, self).__init__(name, parent)
        if path.endswith(os.sep):
            path = path[:-len(os.sep)]
        self.path = path

    def delete(self):
        os.rmdir(self.path)
        super(FolderNode, self).delete()


class FileNode(FileSystemItemNode):

    ctx_actions = ("rename",)
    editor = "text"
    icon = icon_from_res(":/images/file.png")

    def __init__(self, path, name, parent=None):
        super(FileNode, self).__init__(name, parent)
        self.path = path

    def delete(self):
        os.unlink(self.path)
        super(FileNode, self).delete()


class DirTreeNode(TreeNode, FolderNodeMixin):
    
    file_class = FileNode
    folder_class = FolderNode

    def __init__(self, root_dir, parent=None):
        super(DirTreeNode, self).__init__(self.name, parent)
        self.path = root_dir
        folders = {root_dir: self}
        for dirpath, dirnames, filenames in os.walk(root_dir):
            parent = folders[dirpath]
            for dirname in dirnames:
                path = os.path.join(dirpath, dirname)
                folder = self.folder_class(path, dirname)
                folders[os.path.join(dirpath, dirname)] = folder
                parent.add_child(folder)
            for filename in filenames:
                path = os.path.join(dirpath, filename)
                if self.files_filter(filename):
                    parent.add_child(self.file_class(path, 
                        self.file_name(dirpath, filename)))

    def files_filter(self, filename):
        return True

    def file_name(self, dirname, filename):
        return filename
    

__all__ = ["NodeOperationError", "RenameError", "TreeNode",
        "FileSystemItemNode", "FolderNodeMixin", "FolderNode", "FileNode",
        "DirTreeNode"]
