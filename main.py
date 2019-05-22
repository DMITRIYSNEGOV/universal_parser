from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView, QWebEnginePage as QWebPage, QWebEngineSettings as QWebSettings
from mainwindow import Ui_MainWindow  # импорт основной формы
from productwindow import Ui_ProductWindow # импорт формы продукта
from parsedwindow import Ui_ParsedWindow # импорт итоговой формы

from fake_useragent import UserAgent
from requests_html import HTMLSession
# import requests
from bs4 import BeautifulSoup as bs

import platform
import sys
import os
import re
from random import randint
import urllib.parse
from requests.models import PreparedRequest
import time
import math

from selenium import webdriver
import selenium.webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

import csv

class Parser():
    def init_driver(self, type_browser = "firefox64"):
        try:
            if(platform.machine().endswith('64') and type_browser == "firefox"):
                options = webdriver.firefox.options.Options()
                options.add_argument('-headless')
                driver = webdriver.Firefox(service_log_path='NUL', options=options, 
                    executable_path=os.path.join(os.path.abspath(os.curdir),"drivers\\Firefox64\\geckodriver.exe"))
            elif(platform.machine().endswith('32') and type_browser == "firefox"):
                options = webdriver.firefox.options.Options()
                options.add_argument('-headless')
                driver = webdriver.Firefox(service_log_path='NUL', options=options, 
                    executable_path=os.path.join(os.path.abspath(os.curdir),"drivers\\Firefox32\\geckodriver.exe"))                
            elif(type_browser == "edje"):
                driver = webdriver.Edge(executable_path=os.path.join(os.path.abspath(os.curdir),"drivers\\MicrosoftWebDriver.exe"))
            elif(type_browser == "chrome"):
                driver = webdriver.Chrome(executable_path=os.path.join(os.path.abspath(os.curdir),"drivers\\chromedriver.exe"))
            else:
                driver = webdriver.Ie(executable_path=os.path.join(os.path.abspath(os.curdir),"drivers\\IEDriverServer.exe"))
        except Exception as e:
            print(e)
            driver = webdriver.Ie(executable_path=os.path.join(os.path.abspath(os.curdir),"drivers\\IEDriverServer.exe"))
            # driver = webdriver.PhantomJS(os.path.join(os.path.abspath(os.curdir),"drivers\\phantomjs.exe"))
        driver.wait = WebDriverWait(driver, 60)
        return driver

    def wait_for_ajax(self, driver):
        wait = WebDriverWait(driver, 15)
        try:
            wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        except Exception as e:
            print(e)
            pass

    def get_html_code(self, url, type_browser):
        try:
            driver = self.init_driver(type_browser)
            driver.get(url)
            self.wait_for_ajax(driver)
            html_code = driver.page_source
        finally:
            driver.close()
        return html_code


    def get_product_name(self, html_code, product_name):
        soup_product_name = bs(product_name, "html.parser")

        soup_product = bs(html_code, "html.parser")
        product_name_value = soup_product.find(soup_product_name.find().name,
         attrs=soup_product_name.find().attrs).text
        return product_name_value


    def get_list_attrs(self, html_code, html_attr):
        # создаем объекты для парсинга
        soup_product = bs(html_code, "html.parser")
        html_attr = bs(html_attr, "html.parser")
        # находим атрибуты на странице товара
        html_attr = soup_product.find(html_attr.find().name,
            attrs=html_attr.find().attrs)

        # удаляем тэги <br>
        for linebreak in html_attr.find_all('br'):
            linebreak.extract()

        list_attrs = []

        html_list = html_attr.find_all(text=False, recursive=True)
        for i in html_list:
            # поиск внутреннего тега
            while(i.findChildren() != []):
                i= i.findChildren()[0]
            list_attrs.append(i)

            # print("_|_{}_|_".format(i))
            # print("")

        result_list_attr = []
        # извлекаем уникальные теги
        for i in range(0, len(list_attrs)-1):
            if(list_attrs[i]==list_attrs[i+1]):
                continue
            # print(list_attrs[i])
            result_list_attr.append(list_attrs[i])
        # добавляем последний уникальный элемент

        if(result_list_attr == []):
            result_list_attr.append(html_attr)
        elif(result_list_attr[-1] != list_attrs[-1]):
            result_list_attr.append(list_attrs[-1])
        # вывод уникальных тегов с контентом
        # for i in result_list_attr:
        #     print("_|_{}_|_".format(i.text))

        return result_list_attr

class MainProgressBarClass(QThread):
    update_progress_bar = pyqtSignal(int)

    def __init__(self, progress_count):
        super(MainProgressBarClass,self).__init__()
        self.progress_value = math.ceil(100 / progress_count) 

    def run(self):
        self.update_progress_bar.emit(self.progress_value)

class MainThreadClass(QThread, Parser):
    """
    Runs a gathering url thread
    """
    get_list_urls = pyqtSignal(list)

    def __init__(self, progress_bar, section_url, section_tag, product_tag, type_browser, pag_name, pag_from, pag_to, pag_type):
        super(MainThreadClass,self).__init__()
        self.section_url = section_url
        self.section_tag = section_tag
        self.product_tag = product_tag
        self.type_browser = type_browser
        self.pag_name = pag_name
        self.pag_from = pag_from
        self.pag_to = pag_to
        self.pag_type = pag_type
        self.progress_bar = progress_bar

    def update_progress_bar(self, value):
        self.progress_bar.setValue(self.progress_bar.value() + value)

    def get_list_link(self, section_url, section_tag, product_tag, type_browser, pag_name, pag_from, pag_to, pag_type):
        html_code = self.get_html_code(url = section_url, type_browser = type_browser)

        # получить страницу раздела    
        soup_section = bs(section_tag, "lxml")
        # tuple с названием и атрибутами тега раздела (имя, атрибуты)
        section_info = (soup_section.find().name, soup_section.find().attrs)
        soup_product = bs(product_tag, "lxml")
        if "class" in soup_product.find().attrs:
            dict_attr = soup_product.find().attrs
            if isinstance(dict_attr["class"], list):
                class_value = dict_attr["class"][0]
            else:
                class_value = dict_attr["class"]
            list_product = soup_section.find(soup_product.find().name, attrs={"class": class_value})
        else:
            list_product = soup_section.find(soup_product.find().name)
        list_product = list(set(list_product.find_all("a", href=True)))

        url_product_list = []
        for product in list_product:
            product_link = self.get_absolute_url(url=product["href"], section_url=section_url)
            if(self.is_correct_url(product_link)):
                url_product_list.append(product_link)
                print(product_link)
        print(len(list_product))

        if not ((self.pag_name is not None) and (self.pag_from is not None)):
            self.MainProgressBarClass = MainProgressBarClass(1)
            self.MainProgressBarClass.start()
            self.MainProgressBarClass.update_progress_bar.connect(self.update_progress_bar)


        # переход на следующую страницу
        # if self.groupBox_pag.isEnabled():
        if (self.pag_name is not None) and (self.pag_from is not None):
            section_url = re.sub(r"(#\w*)", "", section_url)
            for i in range(pag_from, pag_to+1):
                # ожидание 5-10 секунд
                loop = QEventLoop()
                QTimer.singleShot(randint(5000, 10000), loop.quit)
                loop.exec_()

                #добавить параметр с пагинацией в URL 
                params = {pag_name: i}
                if pag_type == "path":
                    new_url = urllib.parse.urljoin(section_url, "{}{}".format(pag_name, i))
                elif pag_type == "parameter":
                    new_url = self.get_new_pag_url(section_url, params)

                # запрос по URL раздела
                html_code = self.get_html_code(url = new_url, type_browser = type_browser)

                soup_section = bs(html_code, "lxml")
                soup_section = soup_section.find( bs(section_tag, "html.parser").find().name,
                 attrs=bs(section_tag, "html.parser").find().attrs )

                soup_product = bs(product_tag, "html.parser")
                try:
                    if "class" in soup_product.find().attrs:
                        dict_attr = soup_product.find().attrs
                        if isinstance(dict_attr["class"], list):
                            class_value = dict_attr["class"][0]
                        else:
                            class_value = dict_attr["class"]
                        list_product = soup_section.find_all(soup_product.find().name,
                         attrs={"class": class_value})
                    else:
                        list_product = soup_section.find_all(soup_product.find().name)

                except Exception as e:
                    print("ERROR")
                    print(e)
                    break  
                for product in list_product:
                    try:
                        # поиск атрибута href
                        if("href" not in product.attrs):
                            absolute_url = self.get_absolute_url(url=product.find("a", href=True)["href"],
                         section_url=section_url)
                        else:
                            absolute_url = self.get_absolute_url(url=product["href"],
                                section_url=section_url)

                        if(self.is_correct_url(absolute_url)) and (absolute_url not in url_product_list):
                            url_product_list.append(absolute_url)
                            print(absolute_url)
                    except Exception as e:
                        print(e)
                        print(product)
                        raise
                print(len(list_product))

                self.MainProgressBarClass = MainProgressBarClass(pag_to)
                self.MainProgressBarClass.start()
                self.MainProgressBarClass.update_progress_bar.connect(self.update_progress_bar)

        # вывод всех URL товаров и их количество
        url_product_list = list(set(url_product_list))

        for product_url in url_product_list:
            print(product_url)
            # вывод URL продукта в правую панель на главной странице
            # self.url_product_list.appendPlainText(product_url)   
        print(len(url_product_list))

        # возвращаем список URL`ов
        return url_product_list



    def _remove_attrs(self, soup):
        [s.extract() for s in soup('script')]
        for tag in soup.findAll(True): 
            tag.attrs = None
        return soup.body

    def get_absolute_url(self, url, section_url):
        if re.match("^http://|^https://", url):
            return url
        elif re.match(r"^\/", url):
            return "{}{}".format(re.match(r"^(https|http):\/\/(\w|\.|-)*", section_url).group(0), url)
        else:
            return "{}/{}".format(re.match(r"^(https|http):\/\/[^\?]*", section_url).group(0), url)



    def get_new_pag_url(self, section_url, params):
        req = PreparedRequest()
        req.prepare_url(section_url, params)
        return req.url

    def is_correct_url(self, url):
        if len(re.findall(r"(\/\/)", url)) > 1:
            return False
        else:
            return True

    def run(self):
        list_urls = self.get_list_link(
            section_url = self.section_url, 
            section_tag = self.section_tag, 
            product_tag = self.product_tag, 
            type_browser = self.type_browser, 
            pag_name = self.pag_name, 
            pag_from = self.pag_from, 
            pag_to = self.pag_to, 
            pag_type = self.pag_type)
        self.get_list_urls.emit(list_urls)


class mywindow(QtWidgets.QMainWindow, Ui_MainWindow, Parser):
    def __init__(self):
        super(mywindow, self).__init__()
        self.setupUi(self)
        # установка фиксированного окна
        self.setWindowFlags(QtCore.Qt.MSWindowsFixedSizeDialogHint)
        
        # событие нажатия на кнопку получения списков продуктов
        self.get_html_button.clicked.connect(self.start_getting_urls)

        # наличие пагинации
        self.check_is_pag.stateChanged.connect(self.is_pag)

        # событие нажатия на кнопку открытия окна с настройкой продукта
        self.open_product_form.clicked.connect(self.open_product_window)

        # событие проверки доступности нажатия кнопки "Получить ссылки" при вводе
        self.section_url.textChanged.connect(self.validate_input)
        self.section_tag.textChanged.connect(self.validate_input)
        self.product_tag.textChanged.connect(self.validate_input)
        self.pag_name.textChanged.connect(self.validate_input)
        self.pag_to.textChanged.connect(self.validate_input)
        self.pag_from.textChanged.connect(self.validate_input)
        self.check_is_pag.stateChanged.connect(self.validate_input)


    def validate_input(self):
        if not(self.check_is_pag.isChecked()):
            if((self.section_url.text() != "") and 
            (self.section_tag.toPlainText() != "") and 
            (self.product_tag.toPlainText() != "")):
                self.get_html_button.setEnabled(True)
            else:
                self.get_html_button.setEnabled(False)
        else:
            if(self.check_is_pag.isChecked() and 
            self.pag_name.text() != "" and 
            self.pag_to.text() != "" and 
            self.pag_to.text() != "" and 
            self.section_url.text() != "" and 
            self.section_tag.toPlainText() != "" and 
            self.product_tag.toPlainText() != ""):
                self.get_html_button.setEnabled(True)
            else:
                self.get_html_button.setEnabled(False)

    def start_getting_urls(self):
        self.progressBar.setValue(0);
        self.url_product_list.setRowCount(0)

        section_url = self.section_url.text()
        section_tag = self.section_tag.toPlainText()
        product_tag = self.product_tag.toPlainText()

        pag_name = None
        pag_from = None
        pag_to = None
        pag_type = None

        if self.groupBox_pag.isEnabled():
            pag_name = self.pag_name.text()
            pag_from = int(self.pag_from.text())
            pag_to = int(self.pag_to.text())
            if self.radio_pag_type_path.isChecked():
                pag_type = "path"
            else:
                pag_type = "parameter"

        if self.radio_firefox.isChecked():
            type_browser = "firefox"
        elif self.radio_chrome.isChecked():
            type_browser = "chrome"
        elif self.radio_edge.isChecked():
            type_browser = "edje"
        else:
            type_browser = "phantomjs"

        self.MainThreadClass = MainThreadClass(
                                    progress_bar = self.progressBar,
                                    section_url=section_url,
                                    section_tag=section_tag,
                                    product_tag=product_tag,
                                    type_browser=type_browser,
                                    pag_name=pag_name,
                                    pag_from=pag_from,
                                    pag_to=pag_to,
                                    pag_type=pag_type)
        self.MainThreadClass.start()
        self.MainThreadClass.get_list_urls.connect(self.get_list_urls)

    def open_product_window(self):
        list_product_urls = []
        for i in range(self.url_product_list.rowCount()):
            if hasattr(self.url_product_list.item(i, 0), 'text'):
                if self.url_product_list.item(i, 0).text() != "":
                    list_product_urls.append(self.url_product_list.item(i, 0).text())

        if self.radio_firefox.isChecked():
            type_browser = "firefox"
        elif self.radio_chrome.isChecked():
            type_browser = "chrome"
        elif self.radio_edge.isChecked():
            type_browser = "edje"
        else:
            type_browser = "phantomjs"

        self.window = productwindow(list_product_urls, type_browser)
        self.window.show()

    def is_pag(self, state):
        if state == QtCore.Qt.Checked:
            self.groupBox_pag.setEnabled(True)
        else:
            self.groupBox_pag.setEnabled(False)

    def get_list_urls(self, list_urls):
        self.progressBar.setValue(100)

        # диалоговое сообщение о завершении парсинга
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Успешно")
        msg.setText("Получены {} ссылок на товары".format(len(list_urls)))
        msg.exec();
        
        for product_url in list_urls:
            print(product_url)
            # вывод URL продукта в правую панель на главной странице
            row = self.url_product_list.rowCount()
            self.url_product_list.setRowCount(row+1)
            self.url_product_list.setItem(row, 0, QTableWidgetItem(product_url))

        # включаем кнопку "Настроить продукт"
        self.open_product_form.setEnabled(True)

   

class productwindow(QWidget, Ui_ProductWindow, Parser):
    def __init__(self, list_product_urls, type_browser):
        super(productwindow, self).__init__()    
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowIcon(QtGui.QIcon("icon.png"))

        # добавление в первую строку поля для ввода текста
        self.attr_product_list.setCellWidget(0, 0, QtWidgets.QPlainTextEdit())

        # добавление в первую строку радио кнопки
        group = QtWidgets.QGroupBox()
        with_name = QtWidgets.QRadioButton("С названием атрибутов")
        without_name = QtWidgets.QRadioButton("Только значения атрибутов")

        vbox = QVBoxLayout()
        vbox.addWidget(with_name)
        vbox.addWidget(without_name)

        line_attr_name = QtWidgets.QLineEdit()
        line_attr_name.setFixedWidth(350)
        line_attr_name.setFont(QtGui.QFont("Arial", 10))
        line_attr_name.setPlaceholderText("Название атрибута")

        vbox.addWidget(line_attr_name)
        vbox.addStretch(1)
        group.setLayout(vbox)
        self.attr_product_list.setCellWidget(0, 1, group)


        self.type_browser = type_browser
        self.list_product_urls = list_product_urls

        # обработчик кнопки "добавить ячейку"
        self.add_row_button.clicked.connect(self.add_row)

        # обработчик кнопки "получать товары"
        self.get_products_button.clicked.connect(self.open_result_window)

    def add_row(self):
        row = self.attr_product_list.rowCount()
        self.attr_product_list.setRowCount(row + 1)
        
        self.attr_product_list.setCellWidget(row, 0, QtWidgets.QPlainTextEdit())
        
        group = QtWidgets.QGroupBox()
        with_name = QtWidgets.QRadioButton("С названием атрибутов")
        without_name = QtWidgets.QRadioButton("Только значения атрибутов")

        vbox = QVBoxLayout()
        vbox.addWidget(with_name)
        vbox.addWidget(without_name)

        line_attr_name = QtWidgets.QLineEdit()
        line_attr_name.setFixedWidth(350)
        line_attr_name.setFont(QtGui.QFont("Arial", 10))
        line_attr_name.setPlaceholderText("Название атрибута")

        vbox.addWidget(line_attr_name)
        vbox.addStretch(1)
        group.setLayout(vbox)
        self.attr_product_list.setCellWidget(row, 1, group)


    def open_result_window(self):
        # запоминаем все названия и значения атрибутов в виде списка
        # [(key1, value1), (key2, value2), (key3, value3)]
        row = self.attr_product_list.rowCount()
        product_attr_with_params_list = []
        for i in range(row):
            html_attr = self.attr_product_list.cellWidget(i,0).toPlainText()
            if self.attr_product_list.cellWidget(i,1).findChildren(QtWidgets.QRadioButton)[0].isChecked():
                param_attr = "with_name"
            else:
                param_attr = self.attr_product_list.cellWidget(i,1).findChildren(QtWidgets.QLineEdit)[0].text()

            product_attr_with_params_list.append( (html_attr, param_attr) )

        self.window = parsedwindow(
            list_product_urls=self.list_product_urls,
            product_attr_with_params_list=product_attr_with_params_list, 
            type_browser=self.type_browser)
        self.window.show()


class parsedwindow(QWidget, Ui_ParsedWindow, Parser):
    def __init__(self, 
                list_product_urls,
                product_attr_with_params_list, 
                type_browser):
        super(parsedwindow, self).__init__()    
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.MSWindowsFixedSizeDialogHint)
        self.setWindowIcon(QtGui.QIcon("icon.png"))

        self.list_product_urls = list_product_urls
        self.product_attr_with_params_list = product_attr_with_params_list
        self.type_browser = type_browser

        self.get_table(list_product_urls, product_attr_with_params_list, type_browser)

        self.save_2_csv_button.clicked.connect(self.save_to_csv)

    def get_table(self, list_product_urls, product_attr_with_params_list, type_browser):
        
    ##############################################################
    ##############################################################
    ##############################################################
    ##############################################################
        self.result_product_list.setColumnCount(99)
    ##############################################################
    ##############################################################
    ##############################################################
    ##############################################################



        # вывод названий и атрибутов продуктов
        for product_url in list_product_urls:
            try:
                html_code = self.get_html_code(product_url, type_browser)
                # name = self.get_product_name(html_code, product_name)

                row = self.result_product_list.rowCount()
                attr_name_list = ["URL"]
                product_info = [product_url]
                for product_attr in product_attr_with_params_list:
                    product_attr_list = self.get_list_attrs(html_code, product_attr[0])

                    # задаем название атрибутов   
                    for i in range(0, len(product_attr_list)):
                        if(product_attr[1] == "with_name"):
                            if (i%2)==0:
                                attr_name_list.append(product_attr_list[i].text)
                        else:
                            attr_name_list.append(product_attr[1])
                    print(attr_name_list)
                    

                # вывод названия атрибутов в таблицу
                for i in range(0, len(attr_name_list)):
                    self.result_product_list.setRowCount(row+1)
                    
                    self.result_product_list.setItem(row, i, QTableWidgetItem(attr_name_list[i]))

                for product_attr in product_attr_with_params_list:
                    product_attr_list = self.get_list_attrs(html_code, product_attr[0])
                    # задаем значения атрибутов             
                    for i in range(0, len(product_attr_list)):
                        if(product_attr[1] == "with_name"):
                            if(i%2 != 0):
                                print(product_attr_list[i].text)
                                product_info.append(product_attr_list[i].text)
                        else:
                            print(product_attr_list[i].text)
                            product_info.append(product_attr_list[i].text)

                    # выводим значения атрибутов
                    for i in range(0, len(product_info)):
                        self.result_product_list.setRowCount(row+2)
                        # self.result_product_list.setColumnCount(i+1)
                        self.result_product_list.setItem(row+1, i, QTableWidgetItem(product_info[i]))

            except Exception as e:
                print(e)
                print("{} ERROR".format(product_url))


    def save_to_csv(self):
        # записывание атрибутов в csv файл
        with open("test.csv", "a", newline='') as csv_file:
            writer = csv.writer(csv_file)

            row = self.result_product_list.rowCount()
            col = self.result_product_list.columnCount()
            for i in range(row):
                row_attr_list = []
                for j in range(col):
                    if hasattr(self.result_product_list.item(i, j), 'text'):
                        row_attr_list.append(self.result_product_list.item(i, j).text())

                writer.writerow(row_attr_list)
                





app = QtWidgets.QApplication([])
application = mywindow()
application.show()
application.setWindowIcon(QtGui.QIcon("icon.png"))
sys.exit(app.exec())