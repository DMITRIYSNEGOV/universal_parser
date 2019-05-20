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
        ProductWindow.resize(981, 510)
        font = QtGui.QFont()
        font.setFamily("Arial")
        ProductWindow.setFont(font)
        self.attr_product_list = QtWidgets.QTableWidget(ProductWindow)
        self.attr_product_list.setGeometry(QtCore.QRect(10, 10, 961, 441))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(8)
        self.attr_product_list.setFont(font)
        self.attr_product_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.attr_product_list.setWordWrap(False)
        self.attr_product_list.setRowCount(1)
        self.attr_product_list.setColumnCount(2)
        self.attr_product_list.setObjectName("attr_product_list")
        self.attr_product_list.horizontalHeader().setVisible(False)
        self.attr_product_list.horizontalHeader().setCascadingSectionResizes(True)
        self.attr_product_list.horizontalHeader().setDefaultSectionSize(479)
        self.attr_product_list.horizontalHeader().setHighlightSections(True)
        self.attr_product_list.horizontalHeader().setMinimumSectionSize(69)
        self.attr_product_list.verticalHeader().setVisible(False)
        self.attr_product_list.verticalHeader().setDefaultSectionSize(158)
        self.add_row_button = QtWidgets.QPushButton(ProductWindow)
        self.add_row_button.setGeometry(QtCore.QRect(280, 460, 201, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(16)
        self.add_row_button.setFont(font)
        self.add_row_button.setObjectName("add_row_button")
        self.get_products_button = QtWidgets.QPushButton(ProductWindow)
        self.get_products_button.setGeometry(QtCore.QRect(500, 460, 191, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(16)
        self.get_products_button.setFont(font)
        self.get_products_button.setObjectName("get_products_button")

        self.retranslateUi(ProductWindow)
        QtCore.QMetaObject.connectSlotsByName(ProductWindow)

    def retranslateUi(self, ProductWindow):
        _translate = QtCore.QCoreApplication.translate
        ProductWindow.setWindowTitle(_translate("ProductWindow", "Универсальный парсер"))
        self.add_row_button.setText(_translate("ProductWindow", "Добавить  ячейку"))
        self.get_products_button.setText(_translate("ProductWindow", "Получать товары"))


