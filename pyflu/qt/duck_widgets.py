"""
Simple subclasses of basic Qt input widgets that can be manipulated through a
single property.
"""

from PyQt4.QtGui import (QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
        QComboBox)


class ValueLineEdit(QLineEdit):

    @property
    def value(self):
        return self.text()

    @value.setter
    def value(self, value):
        self.setText(value)


class ValueSpinBox(QSpinBox):

    @property
    def value(self):
        return QSpinBox.value(self)

    @value.setter
    def value(self, value):
        self.setValue(value)


class ValueDoubleSpinBox(QDoubleSpinBox):

    @property
    def value(self):
        return QDoubleSpinBox.value(self)

    @value.setter
    def value(self, value):
        self.setValue(value)        


class ValueCheckBox(QCheckBox):

    @property
    def value(self):
        return self.isChecked()

    @value.setter
    def value(self, value):
        self.setChecked(bool(value))


class ValueComboBox(QComboBox):

    use_indices = True
    """
    If :attr:`use_indices` is False, values are stored in the combo box's user
    data rather than indices.
    """

    @property
    def value(self):
        if self.use_indices:
            return self.currentIndex()
        return self.itemData(self.currentIndex()).toPyObject()

    @value.setter
    def value(self, value):
        if self.use_indices:
            self.setCurrentIndex(value)
        else:
            self.setCurrentIndex(self.findData(value))
