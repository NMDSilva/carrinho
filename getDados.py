import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import json
import sqlite3

con = sqlite3.connect('data/carrinho.sqlite')
cur = con.cursor()
url = 'https://mercadao.pt/store/solmar-acores/category/'
# categorias = ['mercearia-11', 'frutas-e-legumes-12', 'talho-13', 'peixaria-14', 'charcutaria-15', 'padaria-e-pastelaria-16', 'take-away-17', 'congelados-18', 'leite-ovos-e-natas-19', 'frigorifico-20', 'alimentacao-equilibrada-21', 'bebidas-22', 'infantil-23', 'higiene-e-beleza-24', 'casa-26', 'animais-27', 'livraria-28']
categorias = ['mercearia-11']

def registarProduto(nomeProduto, imagemProduto, slug):
  for row in cur.execute('SELECT id_produto FROM produtos WHERE slug=:slug', { 'slug': slug }):
    return row[0]
  cur.execute('INSERT INTO produtos VALUES (NULL, ?, ?, ?, ?)', (slug, nomeProduto, imagemProduto, datetime.today().strftime('%Y-%m-%d %H:%M:%S')))
  con.commit()
  return cur.lastrowid

def registarPreco(idProduto, tipoMedida, quantidade, preco):
  cur.execute('INSERT INTO valores VALUES (NULL, ?, ?, ?, ?, ?)', (idProduto, tipoMedida, quantidade, preco, datetime.today().strftime('%Y-%m-%d %H:%M:%S')))
  con.commit()
  return cur.lastrowid

def getMedida(produto):
  if produto.find('DOSE') > 0:
    return int(''.join((ch if ch in '0123456789' else '') for ch in produto))
  if produto.find('UN') > 0:
    return int(''.join((ch if ch in '0123456789' else '') for ch in produto))
  if produto.find('ML') > 0:
    return float(''.join((ch if ch in '0123456789,' else '') for ch in produto).replace(',', '.')) / 1000
  if produto.find('KG') > 0:
    return float(''.join((ch if ch in '0123456789,' else '') for ch in produto).replace(',', '.'))
  if produto.find('MT') > 0:
    return float(''.join((ch if ch in '0123456789,' else '') for ch in produto).replace(',', '.'))
  if produto.find('G') > 0:
    if produto.find('X') > 0:
      q = produto.rsplit('X', 1)
      q[0] = float(''.join((ch if ch in '0123456789,' else '') for ch in q[0]).replace(',', '.'))
      q[1] = float(''.join((ch if ch in '0123456789,' else '') for ch in q[1]).replace(',', '.'))
      return (q[0] * q[1]) / 1000
    else:
      return float(''.join((ch if ch in '0123456789,' else '') for ch in produto).replace(',', '.')) / 1000
  if produto.find('L') > 0:
    return float(''.join((ch if ch in '0123456789,' else '') for ch in produto).replace(',', '.'))

def getTipoMedida(produto):
  if produto.find('DOSE') > 0:
    return 4
  if produto.find('UN') > 0:
    return 1
  if produto.find('ML') > 0:
    return 3
  if produto.find('MT') > 0:
    return 5
  if produto.find('G') > 0:
    return 2
  if produto.find('L') > 0:
    return 3

def navPage(categoria, id):
  driver.get(url + categoria + '?page=' + str(id))
  time.sleep(10)
  element = driver.find_element_by_class_name('_35DP2XbY0vnDR6ntQlSXMJ')
  items = element.find_elements_by_tag_name('pdo-product-item')
  i = 0
  itemsHtml = []
  for item in items:
    itemsHtml.append(item.get_attribute('outerHTML'))
  
  for item in items:
    itemParse = BeautifulSoup(itemsHtml[i], 'html.parser')
    img = itemParse.find('img')
    imagemProduto = img['src'].rsplit('/', 1)[-1]
    nomeProduto = itemParse.find('h3', {'class': 'detail-title'}).text.strip()
    priceUnit = itemParse.find('pdo-product-price-per-unit').text.strip().rsplit('|', 1)
    priceTag = itemParse.find('pdo-product-price-tag').text.strip()
    precoProduto = float(''.join((ch if ch in '0123456789,' else '') for ch in priceTag).replace(',', '.'))

    if priceTag.find('€/Kg') > 0:
      tipoMedida = 2
      quantidadeProduto = 1
    else:
      tipoMedida = getTipoMedida(priceUnit[0].strip())
      quantidadeProduto = getMedida(priceUnit[0].strip())
    print('chegou')
    item.click()
    slug = driver.current_url.rsplit('/', 1)[-1].rsplit('?', 1)[0]
    driver.back()
    time.sleep(5)
    idProduto = registarProduto(nomeProduto, imagemProduto, slug)
    registarPreco(idProduto, tipoMedida, quantidadeProduto, precoProduto)
    i += 1

  return i

option = Options()
option.headless = False
option.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
driver = webdriver.Firefox(options=option)

for categoria in categorias:
  pagina = 0
  print('A correr categoria ' + categoria + ' - Página: ' + str(pagina + 1))
  i = navPage(categoria, pagina)
  while i > 0:
    pagina += 1
    print('A correr categoria ' + categoria + ' - Página: ' + str(pagina + 1))
    i = navPage(categoria, pagina)

con.close()
driver.quit()