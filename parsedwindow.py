# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'parsedwindow.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ParsedWindow(object):
    def setupUi(self, ParsedWindow):
        ParsedWindow.setObjectName("ParsedWindow")
        ParsedWindow.resize(980, 509)
        font = QtGui.QFont()
        font.setFamily("Arial")
        ParsedWindow.setFont(font)
        self.result_product_list = QtWidgets.QTableWidget(ParsedWindow)
        self.result_product_list.setGeometry(QtCore.QRect(10, 10, 961, 451))
        self.result_product_list.setRowCount(0)
        self.result_product_list.setColumnCount(0)
        self.result_product_list.setObjectName("result_product_list")
        self.result_product_list.horizontalHeader().setVisible(False)
        self.result_product_list.horizontalHeader().setHighlightSections(True)
        self.result_product_list.verticalHeader().setVisible(False)
        self.pushButton = QtWidgets.QPushButton(ParsedWindow)
        self.pushButton.setGeometry(QtCore.QRect(320, 470, 331, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(ParsedWindow)
        QtCore.QMetaObject.connectSlotsByName(ParsedWindow)

    def retranslateUi(self, ParsedWindow):
        _translate = QtCore.QCoreApplication.translate
        ParsedWindow.setWindowTitle(_translate("ParsedWindow", "Универсальный парсер"))
        self.pushButton.setText(_translate("ParsedWindow", "Сохранить в CSV"))


