# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'files/qt/bug_report_dialog.ui'
#
# Created: Tue Feb 15 12:08:26 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_BugReportDialog(object):
    def setupUi(self, BugReportDialog):
        BugReportDialog.setObjectName("BugReportDialog")
        BugReportDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        BugReportDialog.resize(683, 620)
        BugReportDialog.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        BugReportDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(BugReportDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_4 = QtGui.QLabel(BugReportDialog)
        font = QtGui.QFont()
        font.setPointSize(17)
        font.setWeight(75)
        font.setBold(True)
        self.label_4.setFont(font)
        self.label_4.setStyleSheet("color: #333;")
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.label = QtGui.QLabel(BugReportDialog)
        self.label.setStyleSheet("margin-bottom: 20px;")
        self.label.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtGui.QLabel(BugReportDialog)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.report_text = QtGui.QPlainTextEdit(BugReportDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.report_text.sizePolicy().hasHeightForWidth())
        self.report_text.setSizePolicy(sizePolicy)
        self.report_text.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.report_text.setObjectName("report_text")
        self.verticalLayout.addWidget(self.report_text)
        self.label_3 = QtGui.QLabel(BugReportDialog)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.traceback_text = QtGui.QTextBrowser(BugReportDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.traceback_text.sizePolicy().hasHeightForWidth())
        self.traceback_text.setSizePolicy(sizePolicy)
        self.traceback_text.setAutoFormatting(QtGui.QTextEdit.AutoBulletList)
        self.traceback_text.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.traceback_text.setOpenExternalLinks(True)
        self.traceback_text.setOpenLinks(False)
        self.traceback_text.setObjectName("traceback_text")
        self.verticalLayout.addWidget(self.traceback_text)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.send_button = QtGui.QPushButton(BugReportDialog)
        self.send_button.setObjectName("send_button")
        self.horizontalLayout.addWidget(self.send_button)
        self.debug_button = QtGui.QPushButton(BugReportDialog)
        self.debug_button.setObjectName("debug_button")
        self.horizontalLayout.addWidget(self.debug_button)
        self.quit_button = QtGui.QPushButton(BugReportDialog)
        self.quit_button.setObjectName("quit_button")
        self.horizontalLayout.addWidget(self.quit_button)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(BugReportDialog)
        QtCore.QObject.connect(self.quit_button, QtCore.SIGNAL("clicked()"), BugReportDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(BugReportDialog)
        BugReportDialog.setTabOrder(self.report_text, self.traceback_text)
        BugReportDialog.setTabOrder(self.traceback_text, self.send_button)
        BugReportDialog.setTabOrder(self.send_button, self.debug_button)
        BugReportDialog.setTabOrder(self.debug_button, self.quit_button)

    def retranslateUi(self, BugReportDialog):
        BugReportDialog.setWindowTitle(QtGui.QApplication.translate("BugReportDialog", "Ooops", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("BugReportDialog", "We are sorry", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("BugReportDialog", "You discovered a bug !", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("BugReportDialog", "Please give us some details about what you were doing:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("BugReportDialog", "Technical details on the incident:", None, QtGui.QApplication.UnicodeUTF8))
        self.send_button.setText(QtGui.QApplication.translate("BugReportDialog", "Send report by e-mail", None, QtGui.QApplication.UnicodeUTF8))
        self.debug_button.setText(QtGui.QApplication.translate("BugReportDialog", "Debug", None, QtGui.QApplication.UnicodeUTF8))
        self.quit_button.setText(QtGui.QApplication.translate("BugReportDialog", "Quit", None, QtGui.QApplication.UnicodeUTF8))
