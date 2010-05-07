from pyflu.qt.models.treenode import TreeNode


class TableNode(TreeNode):

    sub_icons = []
    """
    Icons for sub columns.
    """

    def __init__(self, name=None, sub_names=None, parent=None):
        super(TableNode, self).__init__(name=name, parent=parent) 
        self.sub_names = sub_names if sub_names is not None else []
