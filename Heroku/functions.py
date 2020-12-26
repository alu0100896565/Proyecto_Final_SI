from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
import json
import os
import time
import pandas as pd

NUM_VAL_FAV  = 3
NUM_VAL_BUSQ = 1
NUM_CATEGORIAS_RECOM = 3

defaultTipos = {
    'Todos los departamentos': 0,
    'Alexa Skills': 0,
    'Alimentación y bebidas': 0,
    'Amazon Warehouse': 0,
    'Appstore para Android': 0,
    'Audible audiolibros y podcasts exclusivos': 0,
    'Bebé': 0,
    'Belleza': 0,
    'Bricolaje y herramientas': 0,
    'Cheques regalo': 0,
    'Coche - renting': 0,
    'Coche y Moto - Piezas y accesorios': 0,
    'Deportes y aire libre': 0,
    'Dispositivos de Amazon': 0,
    'Electrónica': 0,
    'Equipaje': 0,
    'Grandes electrodomésticos': 0,
    'Handmade': 0,
    'Hogar y cocina': 0,
    'Iluminación': 0,
    'Industria y ciencia': 0,
    'Informática': 0,
    'Instrumentos musicales': 0,
    'Jardín': 0,
    'Joyería': 0,
    'Juguetes y juegos': 0,
    'Libros': 0,
    'Menos de 10€': 0,
    'Moda': 0,
    'Música Digital': 0,
    'Música: CDs y vinilos': 0,
    'Oficina y papelería': 0,
    'Películas y TV': 0,
    'Prime Video': 0,
    'Productos para mascotas': 0,
    'Relojes': 0,
    'Ropa y accesorios': 0,
    'Salud y cuidado personal': 0,
    'Software': 0,
    'Tienda Kindle': 0,
    'Videojuegos': 0,
    'Zapatos y complementos': 0
}

def SeleniumWS(itemName):
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--no-sandbox")
    # driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    driver = webdriver.Chrome() # usar en local
    busqueda = itemName.replace(' ', '+')
    try:
        driver.get('https://www.google.dz/search?q=' + busqueda + '&tbm=shop')

        # Objeto que guarda el array de items para pasar a JSON
        items = []

        # ps5
        aa = driver.find_elements_by_css_selector('div.sh-dlr__list-result')

        for item in aa:
            itemObj = {}
            itemObj['fotoSrc'] = item.find_element_by_class_name('TL92Hc').get_attribute('src')
            itemObj['name'] = item.find_element_by_class_name('xsRiS').text
            itemObj['price'] = item.find_element_by_class_name('O8U6h').text
            posibleDescripcion = item.find_elements_by_class_name('hBUZL')
            if len(posibleDescripcion) == 2:
                itemObj['description'] = posibleDescripcion[1].text
            else:
                itemObj['description'] = posibleDescripcion[2].text
            itemObj['linkGS'] = item.find_element_by_class_name('FkMp').get_attribute('href')
            items.append(itemObj)

        # botas
        bb = driver.find_elements_by_css_selector('div.sh-dgr__grid-result')

        for item in bb:
            itemObj = {}
            itemObj['name'] = 'NoName'
            itemObj['fotoSrc'] = item.find_element_by_class_name('MUQY0').find_element_by_tag_name('img').get_attribute('src')
            itemObj['price'] = item.find_element_by_class_name('kHxwFf').text
            itemObj['price'] = itemObj['price'].split('\n')[0]
            itemObj['description'] = item.find_element_by_class_name('A2sOrd').text
            itemObj['linkGS'] = item.find_element_by_class_name('ty2Wqb').get_attribute('href')
            items.append(itemObj)
        driver.get('https://www.amazon.es/')
        inputA = driver.find_element_by_id('twotabsearchtextbox')
        inputA.send_keys(itemName)

        actions = ActionChains(driver)
        actions.move_to_element(inputA).perform()
        actions.move_by_offset(40, 70)
        time.sleep(1.5)
        actions.click().perform()
        time.sleep(1)
        sel = Select(driver.find_element_by_tag_name('select'))
        tipo = sel.first_selected_option.text
    finally:
        driver.quit()
    return (items, tipo)

def amazonChar(itemName):
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--no-sandbox")
    # driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    driver = webdriver.Chrome() # usar en local
    driver.get('https://www.amazon.es/')
    inputA = driver.find_element_by_id('twotabsearchtextbox')
    inputA.send_keys(itemName)

    actions = ActionChains(driver)
    actions.move_to_element(inputA).perform()
    actions.move_by_offset(40, 70)
    time.sleep(1.5)
    actions.click().perform()
    time.sleep(1)
    sel = Select(driver.find_element_by_tag_name('select'))
    driver.close()
    return sel.first_selected_option.text

def amazonRecomend(favCategories):
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--no-sandbox")
    # driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    driver = webdriver.Chrome() # usar en local
    resultado = []
    busq = 4
    try:
        for item in favCategories:
            if item[1] == 0:
                continue
            driver.get('https://www.amazon.es/')
            try:
                WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, 'searchDropdownBox')))
            except:
                print("Loading took too much time!")
            categories = driver.find_element_by_id('searchDropdownBox')
            for option in categories.find_elements_by_tag_name('option'):
                if option.text == item[0]:
                    option.click() # select() in earlier versions of webdriver
                    actions = ActionChains(driver)
                    inputA = driver.find_element_by_id('nav-search-submit-text')
                    actions.move_to_element(inputA).perform()
                    actions.click().perform()
                    time.sleep(1)
                    break
            novedades = driver.find_element_by_xpath("//*[contains(text(), 'Novedades destacadas')]").find_element_by_xpath('..').find_element_by_xpath('..')
            amzItems = novedades.find_element_by_tag_name('ul').find_elements_by_tag_name("li")
            for i in range(busq):
                itemCar = {}
                info = amzItems[i].find_element_by_tag_name('a')
                itemCar['name'] = 'NoName'
                itemCar['description'] = info.get_attribute('title')
                itemCar['price'] = amzItems[i].find_element_by_class_name('a-price-whole').text + ' €'
                itemCar['linkGS'] = info.get_attribute('href')
                itemCar['fotoSrc'] = amzItems[i].find_element_by_tag_name('img').get_attribute('src')
                itemCar['tipo'] = item[0]
                resultado.append(itemCar)
            busq -= 1
    finally:
        driver.quit()
    return resultado


def getPandas(usuarios, favoritos, busquedas):
    dictDF = {}
    dictPD = {'usuario': [], 'tipo': [], 'valoracion': []}
    for user in usuarios:
        dictDF[user['username']] = defaultTipos.copy()
    for item in favoritos:
        dictDF[item['usuario']][item['tipo']] += NUM_VAL_FAV
    for item in busquedas:
        dictDF[item['usuario']][item['tipo']] += NUM_VAL_BUSQ
    for user in dictDF:
        for tipo in dictDF[user]:
            dictPD['usuario'].append(user)
            dictPD['tipo'].append(tipo)
            dictPD['valoracion'].append(dictDF[user][tipo])
    valoracionesPD = pd.DataFrame(dictPD)
    return valoracionesPD

def getValUser(favoritos, busquedas):
    dictDF = defaultTipos.copy()
    for item in favoritos:
        dictDF[item['tipo']] += NUM_VAL_FAV
    for item in busquedas:
        dictDF[item['tipo']] += NUM_VAL_BUSQ
    return(sorted(dictDF.items(), key=lambda x: x[1], reverse=True)[:NUM_CATEGORIAS_RECOM])