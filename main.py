from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView, QWebEnginePage as QWebPage, QWebEngineSettings as QWebSettings
from mainwindow import Ui_MainWindow  # импорт основной формы
from productwindow import Ui_ProductWindow # импорт формы продукта
import sys

from fake_useragent import UserAgent
from requests_html import HTMLSession
# import requests
from bs4 import BeautifulSoup as bs

import os
import re
import time
from random import randint
import urllib.parse
from requests.models import PreparedRequest

from selenium import webdriver
import selenium.webdriver
from selenium.webdriver.support.ui import WebDriverWait


def _remove_attrs(soup):
    [s.extract() for s in soup('script')]
    for tag in soup.findAll(True): 
        tag.attrs = None
    return soup.body

def get_absolute_url(url, section_url):
    if re.match("^http://|^https://", url):
        return url
    elif re.match(r"^\/", url):
        return "{}{}".format(re.match(r"^(https|http):\/\/(\w|\.|-)*", section_url).group(0), url)
    else:
        return "{}/{}".format(re.match(r"^(https|http):\/\/[^\?]*", section_url).group(0), url)

def init_driver(type_browser = "phantomjs"):
    try:
        if(type_browser == "firefox32"):
            options = webdriver.firefox.options.Options()
            options.add_argument('-headless')
            driver = webdriver.Firefox(service_log_path='NUL', options=options, executable_path=os.path.join(os.path.abspath(os.curdir),"drivers\\Firefox32\\geckodriver.exe"))
        elif(type_browser == "firefox64"):
            options = webdriver.firefox.options.Options()
            options.add_argument('-headless')
            driver = webdriver.Firefox(service_log_path='NUL', options=options, executable_path=os.path.join(os.path.abspath(os.curdir),"drivers\\Firefox64\\geckodriver.exe"))
        elif(type_browser == "edje"):
            driver = webdriver.Edge(os.path.join(os.path.abspath(os.curdir),"drivers\\MicrosoftWebDriver.exe"))
        else:
            driver = webdriver.PhantomJS(os.path.join(os.path.abspath(os.curdir),"drivers\\phantomjs.exe"))
    except:
        driver = webdriver.PhantomJS(os.path.join(os.path.abspath(os.curdir),"drivers\\phantomjs.exe"))
    driver.wait = WebDriverWait(driver, 60)
    return driver

def wait_for_ajax(driver):
    wait = WebDriverWait(driver, 15)
    try:
        wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    except Exception as e:
        pass

def get_html_code(url, type_browser):
    driver = init_driver(type_browser)
    driver.get(url)
    wait_for_ajax(driver)
    html_code = driver.page_source
    driver.close()
    return html_code

def get_new_pag_url(section_url, params):
    req = PreparedRequest()
    req.prepare_url(section_url, params)
    return req.url

def is_correct_url(url):
    if len(re.findall(r"(\/\/)", url)) > 1:
        return False
    else:
        return True

class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # наличие пагинации
        self.ui.check_is_pag.stateChanged.connect(self.is_pag)

        # событие нажатия на кнопку получения списков продуктов
        self.ui.get_html_button.clicked.connect(self.get_list_link)

        # событие нажатия на кнопку открытия окна с настройкой продукта
        self.ui.open_product_form.clicked.connect(self.open_product_window)

    def open_product_window(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_ProductWindow()
        self.ui.setupUi(self.window)
        self.window.show()

    def is_pag(self, state):
        if state == QtCore.Qt.Checked:
            self.ui.groupBox_pag.setEnabled(True)
        else:
            self.ui.groupBox_pag.setEnabled(False)

    def get_list_link(self):
        section_url = self.ui.section_url.text()
        section_tag = self.ui.section_tag.toPlainText()
        product_tag = self.ui.product_tag.toPlainText()

        if self.ui.groupBox_pag.isEnabled():
            pag_name = self.ui.pag_name.text()
            pag_from = int(self.ui.pag_from.text())
            pag_to = int(self.ui.pag_to.text())
            if self.ui.radio_pag_type_path.isChecked():
                pag_type = "path"
            else:
                pag_type = "parameter"

        if self.ui.radio_firefox32.isChecked():
            type_browser = "firefox32"
        elif self.ui.radio_firefox64.isChecked():
            type_browser = "firefox64"
        elif self.ui.radio_edge.isChecked():
            type_browser = "edje"
        else:
            type_browser = "phantomjs"
        html_code = get_html_code(url = section_url, type_browser = type_browser)

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
            product_link = get_absolute_url(url=product["href"], section_url=section_url)
            if(is_correct_url(product_link)):
                url_product_list.append(product_link)
                print(product_link)
                self.ui.url_product_list.appendPlainText(product_link)
        print(len(list_product))

        # переход на следующую страницу
        if self.ui.groupBox_pag.isEnabled():
            section_url = re.sub(r"(#\w*)", "", section_url)
            for i in range(pag_from, pag_to+1):
                time.sleep(randint(5,10))

                #добавить параметр с пагинацией в URL 
                params = {pag_name: i}
                if pag_type == "path":
                    new_url = urllib.parse.urljoin(section_url, "{}{}".format(pag_name, i))
                elif pag_type == "parameter":
                    new_url = get_new_pag_url(section_url, params)

                # запрос по URL раздела
                html_code = get_html_code(url = new_url, type_browser = type_browser)

                soup_section = bs(html_code, "lxml")
                soup_section = soup_section.find( bs(section_tag, "html.parser").find().name, attrs=bs(section_tag, "html.parser").find().attrs )

                soup_product = bs(product_tag, "html.parser")
                try:
                    if "class" in soup_product.find().attrs:
                        dict_attr = soup_product.find().attrs
                        if isinstance(dict_attr["class"], list):
                            class_value = dict_attr["class"][0]
                        else:
                            class_value = dict_attr["class"]
                        list_product = soup_section.find_all(soup_product.find().name, attrs={"class": class_value})
                    else:
                        list_product = soup_section.find_all(soup_product.find().name)

                except AttributeError:
                    break  
                for product in list_product:
                    try:
                        absolute_url = get_absolute_url(url=product.find("a", href=True)["href"], section_url=section_url)
                        if(is_correct_url(absolute_url)):
                            url_product_list.append(absolute_url)
                            print(absolute_url)
                            self.ui.url_product_list.appendPlainText(absolute_url)
                    except Exception as e:
                        print(e)
                        print(product)
                        raise
                print(len(list_product))

        # вывод всех URL товаров и их количество
        self.ui.url_product_list.clear()
        url_product_list = list(set(url_product_list))
        for i in url_product_list:
            print(i)   
            self.ui.url_product_list.appendPlainText(i)    
        print(len(url_product_list))

app = QtWidgets.QApplication([])
application = mywindow()
application.show()
 
sys.exit(app.exec())