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
        ProductWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(ProductWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(150, 120, 491, 231))
        font = QtGui.QFont()
        font.setPointSize(72)
        self.label.setFont(font)
        self.label.setObjectName("label")
        ProductWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ProductWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        ProductWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ProductWindow)
        self.statusbar.setObjectName("statusbar")
        ProductWindow.setStatusBar(self.statusbar)

        self.retranslateUi(ProductWindow)
        QtCore.QMetaObject.connectSlotsByName(ProductWindow)

    def retranslateUi(self, ProductWindow):
        _translate = QtCore.QCoreApplication.translate
        ProductWindow.setWindowTitle(_translate("ProductWindow", "MainWindow"))
        self.label.setText(_translate("ProductWindow", "CHANGE IT"))


