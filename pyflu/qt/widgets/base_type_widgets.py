"""
Widgets to represent and edit base Python types.
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *


class NumericTypeWidget(object):

    default_minimum = 0
    default_maximum = 1

    def __init__(self, min=None, max=None):
        if min is not None:
            self.setMinimum(min)
        else:
            self.setMinimum(self.default_minimum)
        if max is not None:
            self.setMaximum(max)
        else:
            self.setMaximum(self.default_maximum)

    def get_value(self):
        return self.value()

    def set_value(self, value):
        self.setValue(value)

    widget_value = property(get_value, set_value)


class IntegerTypeWidget(QSpinBox, NumericTypeWidget):

    default_minimum = -999
    default_maximum = 999

    def __init__(self, min=None, max=None, parent=None):
        QSpinBox.__init__(self, parent)
        NumericTypeWidget.__init__(self, min, max)


class FloatTypeWidget(QDoubleSpinBox, NumericTypeWidget):

    default_maximum = 999.0
    default_minimum = -999.0

    def __init__(self, min=None, max=None, parent=None):
        QDoubleSpinBox.__init__(self, parent)
        NumericTypeWidget.__init__(self, min, max)
        self.setDecimals(2)


class StringTypeWidget(QLineEdit):

    def __init__(self, parent=None):
        QLineEdit.__init__(self, parent)

    def get_value(self):
        return unicode(self.text())

    def set_value(self, value):
        self.setText(value)

    widget_value = property(get_value, set_value)


class BooleanTypeWidget(QCheckBox):

    def __init__(self, parent=None):
        QCheckBox.__init__(self, parent)

    def get_value(self):
        return self.isChecked()

    def set_value(self, value):
        self.setChecked(value)

    widget_value = property(get_value, set_value)


class ChoiceTypeWidget(QComboBox):

    EXTRACT_METHODS = {
            int: lambda v: v.toInt()[0],
            float: lambda v: v.toDouble()[0],
            str: lambda v: unicode(v.toString()[0]),
            bool: lambda v: bool(v.toBool()[0]),
        }

    def __init__(self, data_type, choices, parent=None):
        QComboBox.__init__(self, parent)
        self.data_type = data_type
        for value, text in choices:
            self.addItem(text, QVariant(value))

    def get_value(self):
        value = self.itemData(self.currentIndex())
        return self.EXTRACT_METHODS[self.data_type](value)

    def set_value(self, value):
        index = self.findData(QVariant(value))
        if index == -1:
            raise ValueError("invalid value: '%s'" % value)
        self.setCurrentIndex(index)

    widget_value = property(get_value, set_value)


TYPES_WIDGETS = {
    int: IntegerTypeWidget,
    float: FloatTypeWidget,
    str: StringTypeWidget,
    bool: BooleanTypeWidget,
}


def create_type_widget(data_type, choices=None, **kwargs):
    if choices is None:
        return TYPES_WIDGETS[data_type](**kwargs)
    else:
        return ChoiceTypeWidget(data_type, choices, **kwargs)
