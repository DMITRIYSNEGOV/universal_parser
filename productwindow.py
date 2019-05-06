# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'productwindow.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ProductWindow(object):
    def setupUi(self, ProductWindow):
        ProductWindow.setObjectName("ProductWindow")
        ProductWindow.resize(400, 300)
        self.ProductTextEdit = QtWidgets.QPlainTextEdit(ProductWindow)
        self.ProductTextEdit.setGeometry(QtCore.QRect(110, 70, 104, 71))
        self.ProductTextEdit.setObjectName("ProductTextEdit")

        self.retranslateUi(ProductWindow)
        QtCore.QMetaObject.connectSlotsByName(ProductWindow)

    def retranslateUi(self, ProductWindow):
        _translate = QtCore.QCoreApplication.translate
        ProductWindow.setWindowTitle(_translate("ProductWindow", "Form"))


