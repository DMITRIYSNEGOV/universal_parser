# -*- coding: utf-8 -*-
# import socks
# import socket
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
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

import csv
# socks.set_default_proxy(socks.SOCKS5, "localhost", 9150)
# socket.socket = socks.socksocket

# headers = {'User-Agent': UserAgent().chrome}

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

def init_driver(type_browser = "firefox64"):
    try:
        if(type_browser == "firefox32"):
            options = webdriver.firefox.options.Options()
            options.add_argument('-headless')
            driver = webdriver.Firefox(service_log_path='NUL', options=options, 
                executable_path=os.path.join(os.path.abspath(os.curdir),"drivers\\Firefox32\\geckodriver.exe"))
        elif(type_browser == "firefox64"):
            options = webdriver.firefox.options.Options()
            options.add_argument('-headless')
            driver = webdriver.Firefox(service_log_path='NUL', options=options, 
                executable_path=os.path.join(os.path.abspath(os.curdir),"drivers\\Firefox64\\geckodriver.exe"))
        elif(type_browser == "edje"):
            driver = webdriver.Edge(os.path.join(os.path.abspath(os.curdir),"drivers\\MicrosoftWebDriver.exe"))
        else:
            driver = webdriver.PhantomJS(os.path.join(os.path.abspath(os.curdir),"drivers\\phantomjs.exe"))
    except Exception as e:
        print(e)
        driver = webdriver.PhantomJS(os.path.join(os.path.abspath(os.curdir),"drivers\\phantomjs.exe"))
    driver.wait = WebDriverWait(driver, 60)
    return driver

def wait_for_ajax(driver):
    wait = WebDriverWait(driver, 15)
    try:
        wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    except Exception as e:
        print(e)
        pass

def get_html_code(url):
    try:
        driver = init_driver()
        driver.get(url)
        wait_for_ajax(driver)
        html_code = driver.page_source
    finally:
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

def get_product_name(html_code, product_name):
        soup_product_name = bs(product_name, "html.parser")

        soup_product = bs(html_code, "html.parser")
        product_name_value = soup_product.find(soup_product_name.find().name,
         attrs=soup_product_name.find().attrs).text
        return product_name_value

def get_list_attrs(html_code, html_attr):
    # создаем объекты для парсинга
    soup_product = bs(html_code, "html.parser")
    html_attr = bs(html_attr, "html.parser")
    # находим атрибуты на странице товара
    html_attr = soup_product.find(html_attr.find().name,
        attrs=html_attr.find().attrs)

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
    
    # html_code = bs(html_code, "html.parser")
    # attr_key = bs(product_attr_key, "html.parser")
    # list_attr_key = html_code.find_all(attr_key.find().name, attrs=attr_key.attrs)
    # attr_value = bs(product_attr_value, "html.parser")
    # list_attr_value = html_code.find_all(attr_value.find().name, attrs=attr_value.attrs)

    # for i in list_attr_key:
    #     print(i.text)

def get_list_link(section_url, section_tag, product_tag, product_name, product_attr, pag_from, pag_to, pag_name, pag_type):
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
    print(len(list_product))

    # переход на следующую страницу

    section_url = re.sub(r"(#\w*)", "", section_url)
    
        # request_section = session.get(urllib.parse.urljoin(section_url, pagination["value"]), headers = headers, timeout=5)
        # soup_section = bs(request_section.content, "lxml")
        # print(soup_section.find(section_info[0], section_info[1]))
    

    for i in range(pag_from, pag_to+1):
        time.sleep(randint(5,10))

        #добавить параметр с пагинацией в URL 
        params = {pag_name: i}
        if pag_type == "path":
            new_url = urllib.parse.urljoin(section_url, "{}{}".format(pag_name, i))
        elif pag_type == "parameter":
            new_url = get_new_pag_url(section_url, params)

        # запрос по URL раздела
        html_code = get_html_code(new_url)

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
                    absolute_url = get_absolute_url(url=product.find("a", href=True)["href"],
                 section_url=section_url)
                else:
                    absolute_url = get_absolute_url(url=product["href"],
                        section_url=section_url)
                
                if(is_correct_url(absolute_url)):
                    url_product_list.append(absolute_url)
                    print(absolute_url)
            except Exception as e:
                print(e)
                print(product)
                raise
        print(len(list_product))

    # вывод всех URL товаров и их количество
    url_product_list = list(set(url_product_list))
    for product_url in url_product_list:
        print(product_url)       
    print(len(url_product_list))

    # вывод названий и атрибутов продуктов
    product_list = []
    for product_url in url_product_list:
        try:
            html_code = get_html_code(product_url)
            name = get_product_name(html_code, product_name)

            product_attr_list = get_list_attrs(html_code, product_attr)
            product_list.append({"name": name})
            print(name)
            # записывание атрибутов в csv файл
            with open("test.csv", "a", newline='') as csv_file:
                writer = csv.writer(csv_file)

                # задаем название атрбутов
                attr_name = ["URL", "Название"]
                for i in range(0, len(product_attr_list)):
                    if (i%2)==0:
                        attr_name.append(product_attr_list[i].text)

                writer.writerow(attr_name)
                # задаем значения атрибутов
                product_info = [product_url, name]
                for i in range(0, len(product_attr_list)):
                    if(i%2 != 0):
                        print(product_attr_list[i].text)
                        product_info.append(product_attr_list[i].text)
                writer.writerow(product_info)
            print("\n\n")
        except Exception as e:
            print(e)
            print("{} ERROR".format(product_url))
    print(len(product_list))



get_list_link(
            pag_type = "parameter",
            pag_name="page",
            pag_from=1, 
            pag_to=2,
            section_url="http://технология35.рф/product-category/vitriny-kholodilnye-morozilnye-universalnye-konditerskie-dlia-morozhenogo-kassovye-prilavki/",
            section_tag="""<div class="change_products sn-products-container">

<div class="product-card-wide" data-product="14686">
    <a class="product-card-wide-body" href="/product/konditerskaia-kholodilnaia-vitrina-cryspi-vpv-012-08-octava-k-1200-ral-3002-168467-o-vpvk1-120g-3002/">
        
            <div class="product-card-wide-thumb">
                <img class="product-card-wide-thumb__image" src="/media/filer_public_thumbnails/filer_public/c8/17/c8178c31-75dc-4d60-b727-4dc1bdecfc5d/168467.png__150x150_q85_subsampling-2.jpg" alt="Кондитерская холодильная витрина Cryspi ВПВ 0,12-0,8 (Octava К 1200) (RAL 3002)">
                <div class="product-card-wide-preview">
                    <img class="product-card-wide-preview__image" src="/media/filer_public/c8/17/c8178c31-75dc-4d60-b727-4dc1bdecfc5d/168467.png" alt="Кондитерская холодильная витрина Cryspi ВПВ 0,12-0,8 (Octava К 1200) (RAL 3002)">
                </div>
            </div>
        
        <p class="product-card-wide-title">Кондитерская холодильная витрина Cryspi ВПВ 0,12-0,8 (Octava К 1200) (RAL 3002)</p>
        <div class="product-card-wide-prices">
            
                
                    <p class="product-card-wide-price">54 021 руб.</p>
                
            
        </div>
    </a>

    <form class="product-card-wide-form" action="/api/shop/cart/add/" method="POST">
        
        <input type="hidden" name="product-id" value="14686">
        
        
        <div class="badges">
            
            
            
        </div>
        
            <div class="amount">
                <div class="product-amount">
                    <div class="product-amount__button product-amount__button_minus">◄</div>
                    <div class="product-amount__field">
                        <input type="number" name="product-count" min="1" max="100" value="1">
                    </div>
                    <div class="product-amount__button product-amount__button_plus">►</div>
                </div>
            </div>
        
        <div class="product-card-wide-actions">
            <button class="product-card-wide-action-btn sn-add-to-favorites " data-url="/api/shop/favorites/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#heart"></use>
                </svg>
            </button>
            <button class="product-card-wide-action-btn sn-add-to-compare " data-url="/api/shop/compare/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#compare_icon"></use>
                </svg>
            </button>
            
                <div class="product-card-wide-add-cart-wrap">
                    <button class="product-card-wide-add-cart add-to-cart sn-add-to-cart btn btn-outline-primary" type="submit" onclick="ym(52347178, 'reachGoal', 'vkorziny'); return true;">В корзину</button>
                    <div class="go-to-cart">
                        <span>Товар добавлен в корзину</span>
                        <a class="btn btn-primary" onclick="event.stopPropagation()" href="/shop/cart/">Перейти в корзину</a>
                    </div>
                </div>
            
        </div>
    </form>
</div>



<div class="product-card-wide" data-product="14680">
    <a class="product-card-wide-body" href="/product/konditerskaia-kholodilnaia-vitrina-cryspi-vpv-018-122-octava-k-1500-ral-3002-168468-o-vpvk1-150g-3002/">
        
            <div class="product-card-wide-thumb">
                <img class="product-card-wide-thumb__image" src="/media/filer_public_thumbnails/filer_public/d0/fd/d0fd2281-aa8b-4f41-b9f5-ebdf750fbbed/168468.png__150x150_q85_subsampling-2.jpg" alt="Кондитерская холодильная витрина Cryspi ВПВ 0,18-1,22 (Octava К 1500) (RAL 3002)">
                <div class="product-card-wide-preview">
                    <img class="product-card-wide-preview__image" src="/media/filer_public/d0/fd/d0fd2281-aa8b-4f41-b9f5-ebdf750fbbed/168468.png" alt="Кондитерская холодильная витрина Cryspi ВПВ 0,18-1,22 (Octava К 1500) (RAL 3002)">
                </div>
            </div>
        
        <p class="product-card-wide-title">Кондитерская холодильная витрина Cryspi ВПВ 0,18-1,22 (Octava К 1500) (RAL 3002)</p>
        <div class="product-card-wide-prices">
            
                
                    <p class="product-card-wide-price">59 488 руб.</p>
                
            
        </div>
    </a>

    <form class="product-card-wide-form" action="/api/shop/cart/add/" method="POST">
        
        <input type="hidden" name="product-id" value="14680">
        
        
        <div class="badges">
            
            
            
        </div>
        
            <div class="amount">
                <div class="product-amount">
                    <div class="product-amount__button product-amount__button_minus">◄</div>
                    <div class="product-amount__field">
                        <input type="number" name="product-count" min="1" max="100" value="1">
                    </div>
                    <div class="product-amount__button product-amount__button_plus">►</div>
                </div>
            </div>
        
        <div class="product-card-wide-actions">
            <button class="product-card-wide-action-btn sn-add-to-favorites " data-url="/api/shop/favorites/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#heart"></use>
                </svg>
            </button>
            <button class="product-card-wide-action-btn sn-add-to-compare " data-url="/api/shop/compare/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#compare_icon"></use>
                </svg>
            </button>
            
                <div class="product-card-wide-add-cart-wrap">
                    <button class="product-card-wide-add-cart add-to-cart sn-add-to-cart btn btn-outline-primary" type="submit" onclick="ym(52347178, 'reachGoal', 'vkorziny'); return true;">В корзину</button>
                    <div class="go-to-cart">
                        <span>Товар добавлен в корзину</span>
                        <a class="btn btn-primary" onclick="event.stopPropagation()" href="/shop/cart/">Перейти в корзину</a>
                    </div>
                </div>
            
        </div>
    </form>
</div>



<div class="product-card-wide" data-product="14634">
    <a class="product-card-wide-body" href="/product/konditerskaia-kholodilnaia-vitrina-cryspi-vpv-030-154-elegia-k-1240-d-ral-1001-168550-e-vpvk1-124d-1001/">
        
            <div class="product-card-wide-thumb">
                <img class="product-card-wide-thumb__image" src="/media/filer_public_thumbnails/filer_public/6a/77/6a776e5a-18b2-4995-91fe-a589f6197a7c/168550.png__150x150_q85_subsampling-2.jpg" alt="Кондитерская холодильная витрина Cryspi ВПВ 0,30-1,54 (Elegia К 1240 Д) (RAL 1001)">
                <div class="product-card-wide-preview">
                    <img class="product-card-wide-preview__image" src="/media/filer_public/6a/77/6a776e5a-18b2-4995-91fe-a589f6197a7c/168550.png" alt="Кондитерская холодильная витрина Cryspi ВПВ 0,30-1,54 (Elegia К 1240 Д) (RAL 1001)">
                </div>
            </div>
        
        <p class="product-card-wide-title">Кондитерская холодильная витрина Cryspi ВПВ 0,30-1,54 (Elegia К 1240 Д) (RAL 1001)</p>
        <div class="product-card-wide-prices">
            
                
                    <p class="product-card-wide-price">89 109 руб.</p>
                
            
        </div>
    </a>

    <form class="product-card-wide-form" action="/api/shop/cart/add/" method="POST">
        
        <input type="hidden" name="product-id" value="14634">
        
        
        <div class="badges">
            
            
            
        </div>
        
            <div class="amount">
                <div class="product-amount">
                    <div class="product-amount__button product-amount__button_minus">◄</div>
                    <div class="product-amount__field">
                        <input type="number" name="product-count" min="1" max="100" value="1">
                    </div>
                    <div class="product-amount__button product-amount__button_plus">►</div>
                </div>
            </div>
        
        <div class="product-card-wide-actions">
            <button class="product-card-wide-action-btn sn-add-to-favorites " data-url="/api/shop/favorites/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#heart"></use>
                </svg>
            </button>
            <button class="product-card-wide-action-btn sn-add-to-compare " data-url="/api/shop/compare/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#compare_icon"></use>
                </svg>
            </button>
            
                <div class="product-card-wide-add-cart-wrap">
                    <button class="product-card-wide-add-cart add-to-cart sn-add-to-cart btn btn-outline-primary" type="submit" onclick="ym(52347178, 'reachGoal', 'vkorziny'); return true;">В корзину</button>
                    <div class="go-to-cart">
                        <span>Товар добавлен в корзину</span>
                        <a class="btn btn-primary" onclick="event.stopPropagation()" href="/shop/cart/">Перейти в корзину</a>
                    </div>
                </div>
            
        </div>
    </form>
</div>



<div class="product-card-wide" data-product="14673">
    <a class="product-card-wide-body" href="/product/konditerskaia-kholodilnaia-vitrina-cryspi-vpv-052-180-gamma-2-k-1350-ral-3004-168423-g2-vpvk1-135g-3004/">
        
            <div class="product-card-wide-thumb">
                <img class="product-card-wide-thumb__image" src="/media/filer_public_thumbnails/filer_public/97/44/97443ac6-1c2d-4e52-a114-33dc3bfab3cd/168423.png__150x150_q85_subsampling-2.jpg" alt="Кондитерская холодильная витрина Cryspi ВПВ 0,52-1,80 (Gamma-2 К 1350) (RAL 3004)">
                <div class="product-card-wide-preview">
                    <img class="product-card-wide-preview__image" src="/media/filer_public/97/44/97443ac6-1c2d-4e52-a114-33dc3bfab3cd/168423.png" alt="Кондитерская холодильная витрина Cryspi ВПВ 0,52-1,80 (Gamma-2 К 1350) (RAL 3004)">
                </div>
            </div>
        
        <p class="product-card-wide-title">Кондитерская холодильная витрина Cryspi ВПВ 0,52-1,80 (Gamma-2 К 1350) (RAL 3004)</p>
        <div class="product-card-wide-prices">
            
                
                    <p class="product-card-wide-price">59 771 руб.</p>
                
            
        </div>
    </a>

    <form class="product-card-wide-form" action="/api/shop/cart/add/" method="POST">
        
        <input type="hidden" name="product-id" value="14673">
        
        
        <div class="badges">
            
            
            
        </div>
        
            <div class="amount">
                <div class="product-amount">
                    <div class="product-amount__button product-amount__button_minus">◄</div>
                    <div class="product-amount__field">
                        <input type="number" name="product-count" min="1" max="100" value="1">
                    </div>
                    <div class="product-amount__button product-amount__button_plus">►</div>
                </div>
            </div>
        
        <div class="product-card-wide-actions">
            <button class="product-card-wide-action-btn sn-add-to-favorites " data-url="/api/shop/favorites/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#heart"></use>
                </svg>
            </button>
            <button class="product-card-wide-action-btn sn-add-to-compare " data-url="/api/shop/compare/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#compare_icon"></use>
                </svg>
            </button>
            
                <div class="product-card-wide-add-cart-wrap">
                    <button class="product-card-wide-add-cart add-to-cart sn-add-to-cart btn btn-outline-primary" type="submit" onclick="ym(52347178, 'reachGoal', 'vkorziny'); return true;">В корзину</button>
                    <div class="go-to-cart">
                        <span>Товар добавлен в корзину</span>
                        <a class="btn btn-primary" onclick="event.stopPropagation()" href="/shop/cart/">Перейти в корзину</a>
                    </div>
                </div>
            
        </div>
    </form>
</div>



<div class="product-card-wide" data-product="14678">
    <a class="product-card-wide-body" href="/product/konditerskaia-kholodilnaia-vitrina-cryspi-vpv-062-210-gamma-2-k-1600-ral-3004-168453-g2-vpvk1-160g-3004/">
        
            <div class="product-card-wide-thumb">
                <img class="product-card-wide-thumb__image" src="/media/filer_public_thumbnails/filer_public/b3/8d/b38de184-2c42-4bec-ad8b-23f16e774408/168453.png__150x150_q85_subsampling-2.jpg" alt="Кондитерская холодильная витрина Cryspi ВПВ 0,62-2,10 (Gamma-2 К 1600) (RAL 3004)">
                <div class="product-card-wide-preview">
                    <img class="product-card-wide-preview__image" src="/media/filer_public/b3/8d/b38de184-2c42-4bec-ad8b-23f16e774408/168453.png" alt="Кондитерская холодильная витрина Cryspi ВПВ 0,62-2,10 (Gamma-2 К 1600) (RAL 3004)">
                </div>
            </div>
        
        <p class="product-card-wide-title">Кондитерская холодильная витрина Cryspi ВПВ 0,62-2,10 (Gamma-2 К 1600) (RAL 3004)</p>
        <div class="product-card-wide-prices">
            
                
                    <p class="product-card-wide-price">67 965 руб.</p>
                
            
        </div>
    </a>

    <form class="product-card-wide-form" action="/api/shop/cart/add/" method="POST">
        
        <input type="hidden" name="product-id" value="14678">
        
        
        <div class="badges">
            
            
            
        </div>
        
            <div class="amount">
                <div class="product-amount">
                    <div class="product-amount__button product-amount__button_minus">◄</div>
                    <div class="product-amount__field">
                        <input type="number" name="product-count" min="1" max="100" value="1">
                    </div>
                    <div class="product-amount__button product-amount__button_plus">►</div>
                </div>
            </div>
        
        <div class="product-card-wide-actions">
            <button class="product-card-wide-action-btn sn-add-to-favorites " data-url="/api/shop/favorites/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#heart"></use>
                </svg>
            </button>
            <button class="product-card-wide-action-btn sn-add-to-compare " data-url="/api/shop/compare/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#compare_icon"></use>
                </svg>
            </button>
            
                <div class="product-card-wide-add-cart-wrap">
                    <button class="product-card-wide-add-cart add-to-cart sn-add-to-cart btn btn-outline-primary" type="submit" onclick="ym(52347178, 'reachGoal', 'vkorziny'); return true;">В корзину</button>
                    <div class="go-to-cart">
                        <span>Товар добавлен в корзину</span>
                        <a class="btn btn-primary" onclick="event.stopPropagation()" href="/shop/cart/">Перейти в корзину</a>
                    </div>
                </div>
            
        </div>
    </form>
</div>



<div class="product-card-wide" data-product="14650">
    <a class="product-card-wide-body" href="/product/konditerskaia-kholodilnaia-vitrina-enteco-master-viliia-premium-125-vv-ral-3003-254944-viliia-premium-125-vv-3003/">
        
            <div class="product-card-wide-thumb">
                <img class="product-card-wide-thumb__image" src="/media/filer_public_thumbnails/filer_public/a4/8b/a48b415d-1ec7-4c72-afd8-b7952924a9bf/254944.png__150x150_q85_subsampling-2.jpg" alt="Кондитерская холодильная витрина Enteco Master ВИЛИЯ PREMIUM 125 ВВ RAL 3003">
                <div class="product-card-wide-preview">
                    <img class="product-card-wide-preview__image" src="/media/filer_public/a4/8b/a48b415d-1ec7-4c72-afd8-b7952924a9bf/254944.png" alt="Кондитерская холодильная витрина Enteco Master ВИЛИЯ PREMIUM 125 ВВ RAL 3003">
                </div>
            </div>
        
        <p class="product-card-wide-title">Кондитерская холодильная витрина Enteco Master ВИЛИЯ PREMIUM 125 ВВ RAL 3003</p>
        <div class="product-card-wide-prices">
            
                <p class="product-card-wide-no-price">Цена по запросу</p>
            
        </div>
    </a>

    <form class="product-card-wide-form" action="/api/shop/cart/add/" method="POST">
        
        <input type="hidden" name="product-id" value="14650">
        
        
        <div class="badges">
            
            
            
        </div>
        
        <div class="product-card-wide-actions">
            <button class="product-card-wide-action-btn sn-add-to-favorites " data-url="/api/shop/favorites/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#heart"></use>
                </svg>
            </button>
            <button class="product-card-wide-action-btn sn-add-to-compare " data-url="/api/shop/compare/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#compare_icon"></use>
                </svg>
            </button>
            
                <div class="product-card-wide-add-cart-wrap">
                    <div class="product-card-add product-card-add_inverse modal_product_trigger modal_trigger" data-target="#product-nutify">Уведомить</div> 
                </div>
            
        </div>
    </form>
</div>



<div class="product-card-wide" data-product="14716">
    <a class="product-card-wide-body" href="/product/konditerskaia-kholodilnaia-vitrina-enteco-master-nemiga-extra-k-250-vv-ral-3000-246560-nemiga-extra-k-250vv-3000/">
        
            <div class="product-card-wide-thumb">
                <img class="product-card-wide-thumb__image" src="/media/filer_public_thumbnails/filer_public/a2/3a/a23a3b25-30c7-42de-b30c-b8cca6801845/246560.png__150x150_q85_subsampling-2.jpg" alt="Кондитерская холодильная витрина Enteco Master НЕМИГА EXTRA K 250 ВВ RAL 3000">
                <div class="product-card-wide-preview">
                    <img class="product-card-wide-preview__image" src="/media/filer_public/a2/3a/a23a3b25-30c7-42de-b30c-b8cca6801845/246560.png" alt="Кондитерская холодильная витрина Enteco Master НЕМИГА EXTRA K 250 ВВ RAL 3000">
                </div>
            </div>
        
        <p class="product-card-wide-title">Кондитерская холодильная витрина Enteco Master НЕМИГА EXTRA K 250 ВВ RAL 3000</p>
        <div class="product-card-wide-prices">
            
                <p class="product-card-wide-no-price">Цена по запросу</p>
            
        </div>
    </a>

    <form class="product-card-wide-form" action="/api/shop/cart/add/" method="POST">
        
        <input type="hidden" name="product-id" value="14716">
        
        
        <div class="badges">
            
             <span class="badge badge-warning">Хит!</span> 
            
        </div>
        
        <div class="product-card-wide-actions">
            <button class="product-card-wide-action-btn sn-add-to-favorites " data-url="/api/shop/favorites/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#heart"></use>
                </svg>
            </button>
            <button class="product-card-wide-action-btn sn-add-to-compare " data-url="/api/shop/compare/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#compare_icon"></use>
                </svg>
            </button>
            
                <div class="product-card-wide-add-cart-wrap">
                    <div class="product-card-add product-card-add_inverse modal_product_trigger modal_trigger" data-target="#product-nutify">Уведомить</div> 
                </div>
            
        </div>
    </form>
</div>



<div class="product-card-wide" data-product="14821">
    <a class="product-card-wide-body" href="/product/konditerskaia-kholodilnaia-vitrina-eqta-gamma-vpv-052-180-gamma-2-k-1350-ral-1013-o0000049946-g2-vpvk1-135g-eqta-1013/">
        
            <div class="product-card-wide-thumb">
                <img class="product-card-wide-thumb__image" src="/media/filer_public_thumbnails/filer_public/4c/0e/4c0e4f5b-b76a-435f-a6e1-b740037d0bc3/o0000049946.png__150x150_q85_subsampling-2.jpg" alt="Кондитерская холодильная витрина Eqta_Gamma ВПВ 0,52-1,80 (Gamma-2 К 1350) (RAL 1013)">
                <div class="product-card-wide-preview">
                    <img class="product-card-wide-preview__image" src="/media/filer_public/4c/0e/4c0e4f5b-b76a-435f-a6e1-b740037d0bc3/o0000049946.png" alt="Кондитерская холодильная витрина Eqta_Gamma ВПВ 0,52-1,80 (Gamma-2 К 1350) (RAL 1013)">
                </div>
            </div>
        
        <p class="product-card-wide-title">Кондитерская холодильная витрина Eqta_Gamma ВПВ 0,52-1,80 (Gamma-2 К 1350) (RAL 1013)</p>
        <div class="product-card-wide-prices">
            
                
                    <p class="product-card-wide-price">53 048 руб.</p>
                
            
        </div>
    </a>

    <form class="product-card-wide-form" action="/api/shop/cart/add/" method="POST">
        
        <input type="hidden" name="product-id" value="14821">
        
        
        <div class="badges">
            
            
            
        </div>
        
            <div class="amount">
                <div class="product-amount">
                    <div class="product-amount__button product-amount__button_minus">◄</div>
                    <div class="product-amount__field">
                        <input type="number" name="product-count" min="1" max="100" value="1">
                    </div>
                    <div class="product-amount__button product-amount__button_plus">►</div>
                </div>
            </div>
        
        <div class="product-card-wide-actions">
            <button class="product-card-wide-action-btn sn-add-to-favorites " data-url="/api/shop/favorites/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#heart"></use>
                </svg>
            </button>
            <button class="product-card-wide-action-btn sn-add-to-compare " data-url="/api/shop/compare/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#compare_icon"></use>
                </svg>
            </button>
            
                <div class="product-card-wide-add-cart-wrap">
                    <button class="product-card-wide-add-cart add-to-cart sn-add-to-cart btn btn-outline-primary" type="submit" onclick="ym(52347178, 'reachGoal', 'vkorziny'); return true;">В корзину</button>
                    <div class="go-to-cart">
                        <span>Товар добавлен в корзину</span>
                        <a class="btn btn-primary" onclick="event.stopPropagation()" href="/shop/cart/">Перейти в корзину</a>
                    </div>
                </div>
            
        </div>
    </form>
</div>



<div class="product-card-wide" data-product="14822">
    <a class="product-card-wide-body" href="/product/konditerskaia-kholodilnaia-vitrina-eqta-gamma-vpv-052-180-gamma-2-k-1350-ral-3004-o0000048775-g2-vpvk1-135g-eqta-3004/">
        
            <div class="product-card-wide-thumb">
                <img class="product-card-wide-thumb__image" src="/media/filer_public_thumbnails/filer_public/85/25/852553f4-66ce-4b4a-b3be-6329ed940f99/o0000048775.png__150x150_q85_subsampling-2.jpg" alt="Кондитерская холодильная витрина Eqta_Gamma ВПВ 0,52-1,80 (Gamma-2 К 1350) (RAL 3004)">
                <div class="product-card-wide-preview">
                    <img class="product-card-wide-preview__image" src="/media/filer_public/85/25/852553f4-66ce-4b4a-b3be-6329ed940f99/o0000048775.png" alt="Кондитерская холодильная витрина Eqta_Gamma ВПВ 0,52-1,80 (Gamma-2 К 1350) (RAL 3004)">
                </div>
            </div>
        
        <p class="product-card-wide-title">Кондитерская холодильная витрина Eqta_Gamma ВПВ 0,52-1,80 (Gamma-2 К 1350) (RAL 3004)</p>
        <div class="product-card-wide-prices">
            
                
                    <p class="product-card-wide-price">52 013 руб.</p>
                
            
        </div>
    </a>

    <form class="product-card-wide-form" action="/api/shop/cart/add/" method="POST">
        
        <input type="hidden" name="product-id" value="14822">
        
        
        <div class="badges">
            
            
            
        </div>
        
            <div class="amount">
                <div class="product-amount">
                    <div class="product-amount__button product-amount__button_minus">◄</div>
                    <div class="product-amount__field">
                        <input type="number" name="product-count" min="1" max="100" value="1">
                    </div>
                    <div class="product-amount__button product-amount__button_plus">►</div>
                </div>
            </div>
        
        <div class="product-card-wide-actions">
            <button class="product-card-wide-action-btn sn-add-to-favorites " data-url="/api/shop/favorites/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#heart"></use>
                </svg>
            </button>
            <button class="product-card-wide-action-btn sn-add-to-compare " data-url="/api/shop/compare/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#compare_icon"></use>
                </svg>
            </button>
            
                <div class="product-card-wide-add-cart-wrap">
                    <button class="product-card-wide-add-cart add-to-cart sn-add-to-cart btn btn-outline-primary" type="submit" onclick="ym(52347178, 'reachGoal', 'vkorziny'); return true;">В корзину</button>
                    <div class="go-to-cart">
                        <span>Товар добавлен в корзину</span>
                        <a class="btn btn-primary" onclick="event.stopPropagation()" href="/shop/cart/">Перейти в корзину</a>
                    </div>
                </div>
            
        </div>
    </form>
</div>



<div class="product-card-wide" data-product="14823">
    <a class="product-card-wide-body" href="/product/konditerskaia-kholodilnaia-vitrina-eqta-gamma-vpv-062-210-gamma-2-k-1600-ral-1013-o0000049947-g2-vpvk1-160g-eqta-1013/">
        
            <div class="product-card-wide-thumb">
                <img class="product-card-wide-thumb__image" src="/media/filer_public_thumbnails/filer_public/ed/1a/ed1a1c0d-047e-4658-a74d-78c9b0a36db4/o0000049947.png__150x150_q85_subsampling-2.jpg" alt="Кондитерская холодильная витрина Eqta_Gamma ВПВ 0,62-2,10 (Gamma-2 К 1600) (RAL 1013)">
                <div class="product-card-wide-preview">
                    <img class="product-card-wide-preview__image" src="/media/filer_public/ed/1a/ed1a1c0d-047e-4658-a74d-78c9b0a36db4/o0000049947.png" alt="Кондитерская холодильная витрина Eqta_Gamma ВПВ 0,62-2,10 (Gamma-2 К 1600) (RAL 1013)">
                </div>
            </div>
        
        <p class="product-card-wide-title">Кондитерская холодильная витрина Eqta_Gamma ВПВ 0,62-2,10 (Gamma-2 К 1600) (RAL 1013)</p>
        <div class="product-card-wide-prices">
            
                
                    <p class="product-card-wide-price">60 320 руб.</p>
                
            
        </div>
    </a>

    <form class="product-card-wide-form" action="/api/shop/cart/add/" method="POST">
        
        <input type="hidden" name="product-id" value="14823">
        
        
        <div class="badges">
            
            
            
        </div>
        
            <div class="amount">
                <div class="product-amount">
                    <div class="product-amount__button product-amount__button_minus">◄</div>
                    <div class="product-amount__field">
                        <input type="number" name="product-count" min="1" max="100" value="1">
                    </div>
                    <div class="product-amount__button product-amount__button_plus">►</div>
                </div>
            </div>
        
        <div class="product-card-wide-actions">
            <button class="product-card-wide-action-btn sn-add-to-favorites " data-url="/api/shop/favorites/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#heart"></use>
                </svg>
            </button>
            <button class="product-card-wide-action-btn sn-add-to-compare " data-url="/api/shop/compare/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#compare_icon"></use>
                </svg>
            </button>
            
                <div class="product-card-wide-add-cart-wrap">
                    <button class="product-card-wide-add-cart add-to-cart sn-add-to-cart btn btn-outline-primary" type="submit" onclick="ym(52347178, 'reachGoal', 'vkorziny'); return true;">В корзину</button>
                    <div class="go-to-cart">
                        <span>Товар добавлен в корзину</span>
                        <a class="btn btn-primary" onclick="event.stopPropagation()" href="/shop/cart/">Перейти в корзину</a>
                    </div>
                </div>
            
        </div>
    </form>
</div>



<div class="product-card-wide" data-product="14824">
    <a class="product-card-wide-body" href="/product/konditerskaia-kholodilnaia-vitrina-eqta-gamma-vpv-062-210-gamma-2-k-1600-ral-3004-o0000048776-g2-vpvk1-160g-eqta-3004/">
        
            <div class="product-card-wide-thumb">
                <img class="product-card-wide-thumb__image" src="/media/filer_public_thumbnails/filer_public/f1/f3/f1f39d43-ecc0-4309-bd20-d94a48277197/o0000048776.png__150x150_q85_subsampling-2.jpg" alt="Кондитерская холодильная витрина Eqta_Gamma ВПВ 0,62-2,10 (Gamma-2 К 1600) (RAL 3004)">
                <div class="product-card-wide-preview">
                    <img class="product-card-wide-preview__image" src="/media/filer_public/f1/f3/f1f39d43-ecc0-4309-bd20-d94a48277197/o0000048776.png" alt="Кондитерская холодильная витрина Eqta_Gamma ВПВ 0,62-2,10 (Gamma-2 К 1600) (RAL 3004)">
                </div>
            </div>
        
        <p class="product-card-wide-title">Кондитерская холодильная витрина Eqta_Gamma ВПВ 0,62-2,10 (Gamma-2 К 1600) (RAL 3004)</p>
        <div class="product-card-wide-prices">
            
                
                    <p class="product-card-wide-price">59 144 руб.</p>
                
            
        </div>
    </a>

    <form class="product-card-wide-form" action="/api/shop/cart/add/" method="POST">
        
        <input type="hidden" name="product-id" value="14824">
        
        
        <div class="badges">
            
            
            
        </div>
        
            <div class="amount">
                <div class="product-amount">
                    <div class="product-amount__button product-amount__button_minus">◄</div>
                    <div class="product-amount__field">
                        <input type="number" name="product-count" min="1" max="100" value="1">
                    </div>
                    <div class="product-amount__button product-amount__button_plus">►</div>
                </div>
            </div>
        
        <div class="product-card-wide-actions">
            <button class="product-card-wide-action-btn sn-add-to-favorites " data-url="/api/shop/favorites/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#heart"></use>
                </svg>
            </button>
            <button class="product-card-wide-action-btn sn-add-to-compare " data-url="/api/shop/compare/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#compare_icon"></use>
                </svg>
            </button>
            
                <div class="product-card-wide-add-cart-wrap">
                    <button class="product-card-wide-add-cart add-to-cart sn-add-to-cart btn btn-outline-primary" type="submit" onclick="ym(52347178, 'reachGoal', 'vkorziny'); return true;">В корзину</button>
                    <div class="go-to-cart">
                        <span>Товар добавлен в корзину</span>
                        <a class="btn btn-primary" onclick="event.stopPropagation()" href="/shop/cart/">Перейти в корзину</a>
                    </div>
                </div>
            
        </div>
    </form>
</div>



<div class="product-card-wide" data-product="14798">
    <a class="product-card-wide-body" href="/product/konditerskaia-kholodilnaia-vitrina-eqta-gusto-vpv-026-123-t-m-eqta-gusto-k-850-d-ral-9001-o0000044546-gu-eqt-vpvk1-85d-9001/">
        
            <div class="product-card-wide-thumb">
                <img class="product-card-wide-thumb__image" src="/media/filer_public_thumbnails/filer_public/66/05/6605b20c-4925-43fd-9e7a-9eec774e516e/o0000044546.png__150x150_q85_subsampling-2.jpg" alt="Кондитерская холодильная витрина Eqta_Gusto ВПВ 0,26-1,23 (т.м.EQTA Gusto К 850 Д) (RAL 9001)">
                <div class="product-card-wide-preview">
                    <img class="product-card-wide-preview__image" src="/media/filer_public/66/05/6605b20c-4925-43fd-9e7a-9eec774e516e/o0000044546.png" alt="Кондитерская холодильная витрина Eqta_Gusto ВПВ 0,26-1,23 (т.м.EQTA Gusto К 850 Д) (RAL 9001)">
                </div>
            </div>
        
        <p class="product-card-wide-title">Кондитерская холодильная витрина Eqta_Gusto ВПВ 0,26-1,23 (т.м.EQTA Gusto К 850 Д) (RAL 9001)</p>
        <div class="product-card-wide-prices">
            
                
                    <p class="product-card-wide-price">72 454 руб.</p>
                
            
        </div>
    </a>

    <form class="product-card-wide-form" action="/api/shop/cart/add/" method="POST">
        
        <input type="hidden" name="product-id" value="14798">
        
        
        <div class="badges">
            
            
            
        </div>
        
            <div class="amount">
                <div class="product-amount">
                    <div class="product-amount__button product-amount__button_minus">◄</div>
                    <div class="product-amount__field">
                        <input type="number" name="product-count" min="1" max="100" value="1">
                    </div>
                    <div class="product-amount__button product-amount__button_plus">►</div>
                </div>
            </div>
        
        <div class="product-card-wide-actions">
            <button class="product-card-wide-action-btn sn-add-to-favorites " data-url="/api/shop/favorites/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#heart"></use>
                </svg>
            </button>
            <button class="product-card-wide-action-btn sn-add-to-compare " data-url="/api/shop/compare/add" type="button">
                <svg class="product-card-wide-action-btn__icon" role="img">
                    <use xlink:href="/static/images/sprite.svg#compare_icon"></use>
                </svg>
            </button>
            
                <div class="product-card-wide-add-cart-wrap">
                    <button class="product-card-wide-add-cart add-to-cart sn-add-to-cart btn btn-outline-primary" type="submit" onclick="ym(52347178, 'reachGoal', 'vkorziny'); return true;">В корзину</button>
                    <div class="go-to-cart">
                        <span>Товар добавлен в корзину</span>
                        <a class="btn btn-primary" onclick="event.stopPropagation()" href="/shop/cart/">Перейти в корзину</a>
                    </div>
                </div>
            
        </div>
    </form>
</div>

</div>""",
            product_tag = """<a class="product-card-wide-body" href="/product/konditerskaia-kholodilnaia-vitrina-eqta-gusto-vpv-026-123-t-m-eqta-gusto-k-850-d-ral-9001-o0000044546-gu-eqt-vpvk1-85d-9001/">
        
            <div class="product-card-wide-thumb">
                <img class="product-card-wide-thumb__image" src="/media/filer_public_thumbnails/filer_public/66/05/6605b20c-4925-43fd-9e7a-9eec774e516e/o0000044546.png__150x150_q85_subsampling-2.jpg" alt="Кондитерская холодильная витрина Eqta_Gusto ВПВ 0,26-1,23 (т.м.EQTA Gusto К 850 Д) (RAL 9001)">
                <div class="product-card-wide-preview">
                    <img class="product-card-wide-preview__image" src="/media/filer_public/66/05/6605b20c-4925-43fd-9e7a-9eec774e516e/o0000044546.png" alt="Кондитерская холодильная витрина Eqta_Gusto ВПВ 0,26-1,23 (т.м.EQTA Gusto К 850 Д) (RAL 9001)">
                </div>
            </div>
        
        <p class="product-card-wide-title">Кондитерская холодильная витрина Eqta_Gusto ВПВ 0,26-1,23 (т.м.EQTA Gusto К 850 Д) (RAL 9001)</p>
        <div class="product-card-wide-prices">
            
                
                    <p class="product-card-wide-price">72 454 руб.</p>
                
            
        </div>
    </a>""",
            product_name = """<p class="page-title product-form__title" itemprop="name">Кондитерская холодильная витрина Eqta_Gusto ВПВ 0,26-1,23 (т.м.EQTA Gusto К 850 Д) (RAL 9001)</p>""",
            product_attr = """<div class="tab-pane__characteristics">
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Страна</b>
                                            <span class="tab-pane__characteristic-row-value">Россия</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Высота (мм)</b>
                                            <span class="tab-pane__characteristic-row-value">1314</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Ширина (мм)</b>
                                            <span class="tab-pane__characteristic-row-value">764</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Длина (мм)</b>
                                            <span class="tab-pane__characteristic-row-value">852</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Энергопотребление (кВтсутки)</b>
                                            <span class="tab-pane__characteristic-row-value">8,23</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Холодопроизводительность (кВт)</b>
                                            <span class="tab-pane__characteristic-row-value">0,482</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Хладагент</b>
                                            <span class="tab-pane__characteristic-row-value">R404a</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Тип охлаждения</b>
                                            <span class="tab-pane__characteristic-row-value">Динамическое</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Тип агрегата</b>
                                            <span class="tab-pane__characteristic-row-value">Встроенный</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Способ установки</b>
                                            <span class="tab-pane__characteristic-row-value">Напольный</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Площадь экспозиции (м2)</b>
                                            <span class="tab-pane__characteristic-row-value">1,23</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Оттайка</b>
                                            <span class="tab-pane__characteristic-row-value">Автоматическая</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Напряжение (В)</b>
                                            <span class="tab-pane__characteristic-row-value">220</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Наличие подсветки</b>
                                            <span class="tab-pane__characteristic-row-value">Да</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Наличие ночных шторок</b>
                                            <span class="tab-pane__characteristic-row-value">Нет</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Наличие запасника</b>
                                            <span class="tab-pane__characteristic-row-value">Нет</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Назначение витрин</b>
                                            <span class="tab-pane__characteristic-row-value">Кондитерская</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Мощность (Вт)</b>
                                            <span class="tab-pane__characteristic-row-value">626</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Компрессор</b>
                                            <span class="tab-pane__characteristic-row-value">Aspera</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Количество полок</b>
                                            <span class="tab-pane__characteristic-row-value">3</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Гарантия</b>
                                            <span class="tab-pane__characteristic-row-value">12</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Габариты в упаковке (мм)</b>
                                            <span class="tab-pane__characteristic-row-value">1050x990x1475</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">Бренд</b>
                                            <span class="tab-pane__characteristic-row-value">Eqta_Gusto</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">T (min)</b>
                                            <span class="tab-pane__characteristic-row-value">1</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">T (max)</b>
                                            <span class="tab-pane__characteristic-row-value">10</span>
                                        </div>
                                
                                    <div class="tab-pane__characteristic-row">
                                            <b class="tab-pane__characteristic-row-title">RAL</b>
                                            <span class="tab-pane__characteristic-row-value">9001</span>
                                        </div>
                                
                            </div>"""
            )