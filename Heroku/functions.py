from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os

def SeleniumWS(itemName):
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--no-sandbox")
    # driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    driver = webdriver.Chrome() # usar en local
    busqueda = itemName.replace(' ', '+')
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
        itemObj['fotoSrc'] = item.find_element_by_class_name('MUQY0').find_element_by_tag_name('img').get_attribute('src')
        itemObj['price'] = item.find_element_by_class_name('kHxwFf').text
        itemObj['description'] = item.find_element_by_class_name('A2sOrd').text
        itemObj['linkGS'] = item.find_element_by_class_name('ty2Wqb').get_attribute('href')
        items.append(itemObj)

    driver.quit()
    return items

