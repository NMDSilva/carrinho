import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import json
import sqlite3

con = sqlite3.connect('data/carrinho.sqlite')
cur = con.cursor()
url = 'https://mercadao.pt/store/solmar-acores/category/'
idLoja = 1
categorias = []

def inserirCategoria(categoria, link):
  global idLoja
  idCategoria = 0
  for row in cur.execute('SELECT id_categoria FROM categorias WHERE link=:link AND id_loja=:id_loja', { 'link': link, 'id_loja': idLoja }):
    idCategoria = row[0]

  if idCategoria == 0:
    print('Nova categoria encontrada: ' + categoria)
    cur.execute('INSERT INTO categorias VALUES (NULL, ?, ?, ?)', (categoria, link, idLoja))
    con.commit()
    idCategoria = cur.lastrowid

  return [idCategoria, link]

def carregarCategorias():
  global categorias
  global idLoja
  driver.get(url)
  try:
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//pdo-drilldown-list//a")))
    driver.find_element_by_xpath("//pdo-cookies-policy//button").click()
    categoriasElement = driver.find_elements_by_xpath("//pdo-drilldown//pdo-drilldown-list[1]//li")
    del categoriasElement[0]
  except Exception as e:
    print('Não existem categorias')
    return []

  totalCategorias = len(categoriasElement)

  for x in range(totalCategorias):
    categoria = BeautifulSoup(categoriasElement[x].get_attribute('outerHTML'), 'html.parser').find('span').text
    driver.find_element_by_xpath("//pdo-drilldown//pdo-drilldown-list[1]//li[" + str(x + 2) + "]//a").click()
    time.sleep(5)

    try:
      driver.find_element_by_xpath("//pdo-drilldown//pdo-drilldown-list[2]//li[3]//a").click()
    except Exception as e:
      a = 0
      
    linkCategoria = driver.current_url.rsplit('/', 1)[-1]
    driver.get(url)
    categorias.append(inserirCategoria(categoria, linkCategoria))

    try:
      WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//pdo-drilldown-list//a")))
      categoriasElement = driver.find_elements_by_xpath("//pdo-drilldown//pdo-drilldown-list[1]//li")
      del categoriasElement[0]
    except Exception as e:
      print('problemas')

  return categorias

def registarProduto(idCategoria, idMedida, nomeProduto, quantidade, imagemProduto, slug, preco):
  global idLoja
  idProduto = 0
  for row in cur.execute('SELECT id_produto FROM produtos WHERE slug=:slug', { 'slug': slug }):
    idProduto = row[0]

  if idProduto == 0:
    print('Novo produto encontrado: ' + nomeProduto)
    cur.execute('INSERT INTO produtos VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)', (idCategoria, idMedida, idLoja, nomeProduto, quantidade, imagemProduto, slug, datetime.today().strftime('%Y-%m-%d %H:%M:%S')))
    con.commit()
    idProduto = cur.lastrowid

  for row in cur.execute("SELECT COUNT(*) FROM precos WHERE id_produto = :id_produto AND datetime(data_registo) < datetime('now', '-10 hours')", { 'id_produto': idProduto }):
    if row[0] == 0:
      print('Registando preço do produto: ' + nomeProduto)
      cur.execute('INSERT INTO precos VALUES (NULL, ?, ?, ?)', (idProduto, preco, datetime.today().strftime('%Y-%m-%d %H:%M:%S')))
      con.commit()

def getTipoMedida(produto):
  if produto.find('DOSE') > 0:
    return [4, int(''.join((ch if ch in '0123456789' else '') for ch in produto))]
  if produto.find('UN') > 0:
    return [1, int(''.join((ch if ch in '0123456789' else '') for ch in produto))]
  if produto.find('ML') > 0:
    return [3, float(''.join((ch if ch in '0123456789,' else '') for ch in produto).replace(',', '.')) / 1000]
  if produto.find('KG') > 0:
    return [2, float(''.join((ch if ch in '0123456789,' else '') for ch in produto).replace(',', '.'))]
  if produto.find('MT') > 0:
    return [5, float(''.join((ch if ch in '0123456789,' else '') for ch in produto).replace(',', '.'))]
  if produto.find('G') > 0:
    if produto.find('X') > 0:
      q = produto.rsplit('X', 1)
      q[0] = float(''.join((ch if ch in '0123456789,' else '') for ch in q[0]).replace(',', '.'))
      q[1] = float(''.join((ch if ch in '0123456789,' else '') for ch in q[1]).replace(',', '.'))
      return [2, (q[0] * q[1]) / 1000]
    else:
      return [2, float(''.join((ch if ch in '0123456789,' else '') for ch in produto).replace(',', '.')) / 1000]
  if produto.find('L') > 0:
    return [3, float(''.join((ch if ch in '0123456789,' else '') for ch in produto).replace(',', '.'))]

def navPage(categoria, pagina):
  linkNavegacao = url + categoria[1] + '?page=' + str(pagina)
  driver.get(linkNavegacao)
  try:
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, '_35DP2XbY0vnDR6ntQlSXMJ')]")))
    items = driver.find_elements_by_xpath("//pdo-product-item[contains(@class, 'P9eg53AkHYfXRP7gt5njS')]")
  except Exception as e:
    print('Finalizou a procura na categoria: ' + categoria[1])
    items = []

  quantidadeProdutos = len(items)
  if quantidadeProdutos == 0:
    return 0

  for x in range(quantidadeProdutos):
    items[x].click()
    try:
      WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//pdo-cart-button[contains(@class, 'IInJYhj8UtwqbWVpRZwJL')]")))
      produto = driver.find_elements_by_xpath("//div[contains(@class, '_1h2Mufz8maB8iECYl6rnpW')]")[0]
    except Exception as e:
      print('Não foi possível carregar o produto da categoria: ' + categoria[1] + ', página: ' + str(pagina) + ', produto: ' + str(x))
      driver.get(linkNavegacao)
      try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, '_35DP2XbY0vnDR6ntQlSXMJ')]")))
        items = driver.find_elements_by_xpath("//pdo-product-item[contains(@class, 'P9eg53AkHYfXRP7gt5njS')]")
      except Exception as e:
        print('Erro categoria: ' + categoria[1] + ' - linha 137')
        break
      continue

    slug = driver.current_url.rsplit('/', 1)[-1].rsplit('?', 1)[0]
    produtoParse = BeautifulSoup(produto.get_attribute('outerHTML'), 'html.parser')
    imagemProduto = produtoParse.find('picture').find('img')['src'].rsplit('/', 1)[-1]
    priceUnit = produtoParse.find('pdo-product-price-per-unit').text.strip().rsplit('|', 1)[0].strip()
    nomeProduto = produtoParse.find('h2', {'class': '_3MDF8HVHJABdafDgo7eFwa'}).text.strip()
    priceTag = produtoParse.find('pdo-product-price-tag').find('span').text.strip()
    precoProduto = float(''.join((ch if ch in '0123456789,' else '') for ch in priceTag).replace(',', '.'))

    if priceTag.find('€/Kg') > 0:
      tipoMedida = 2
      quantidadeProduto = 1
    else:
      dadosMedida = getTipoMedida(priceUnit)
      tipoMedida = dadosMedida[0]
      quantidadeProduto = dadosMedida[1]

    registarProduto(categoria[0], tipoMedida, nomeProduto, quantidadeProduto, imagemProduto, slug, precoProduto)
    
    driver.back()
    try:
      WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, '_35DP2XbY0vnDR6ntQlSXMJ')]")))
      items = driver.find_elements_by_xpath("//pdo-product-item[contains(@class, 'P9eg53AkHYfXRP7gt5njS')]")
    except Exception as e:
      print('Erro categoria: ' + categoria[1] + ' - linha 164')
  
  return quantidadeProdutos

try:
  inicial = datetime.now()
  print('Tarefa iniciou - ' + inicial.strftime('%Y-%m-%d %H:%M:%S'))
  option = Options()
  option.headless = True
  option.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
  driver = webdriver.Firefox(options=option)
  print('Iniciar verificação de Categorias')
  categorias = carregarCategorias()
  
  print('Iniciar carregamento de produtos')
  for categoria in categorias:
    pagina = 0
    print('A correr categoria ' + categoria[1] + ', página: ' + str(pagina + 1))
    i = navPage(categoria, pagina)

    while i > 0:
      pagina += 1
      print('A correr categoria ' + categoria[1] + ', página: ' + str(pagina + 1))
      i = navPage(categoria, pagina)

finally:
  con.close()
  driver.quit()
  final = datetime.now()
  print('Tarefa terminou - ' + final.strftime('%Y-%m-%d %H:%M:%S'))
  tempoSegundos = (final - inicial).total_seconds()
  horas = divmod(tempoSegundos, 3600)
  minutos = divmod(horas[1], 60)
  segundos = divmod(minutos[1], 1)

  print('Tempo de execução: %d horas, %d minutos e %d segundos' % (horas[0], minutos[0], segundos[0]))
