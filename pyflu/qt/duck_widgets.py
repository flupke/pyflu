"""
Simple subclasses of basic Qt input widgets that can be manipulated through a
single property.
"""

from PyQt4.QtGui import QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox


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
