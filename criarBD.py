import os
import sqlite3
os.remove('data/carrinho.sqlite')

con = sqlite3.connect('data/carrinho.sqlite')
cur = con.cursor()

cur.execute('CREATE TABLE "lojas" ("id_loja" INTEGER, "loja" INTEGER UNIQUE, "url_imgs" TEXT, PRIMARY KEY("id_loja" AUTOINCREMENT))')
cur.execute('CREATE TABLE "produtos" ("id_produto" INTEGER, "id_categoria" INTEGER, "id_medida" INTEGER NOT NULL, "id_loja" INTEGER, "nome_produto" TEXT NOT NULL, "quantidade" INTEGER, "img" TEXT, "slug" TEXT NOT NULL, "data_registo" TEXT, PRIMARY KEY("id_produto" AUTOINCREMENT))')
cur.execute('CREATE TABLE "categorias" ("id_categoria" INTEGER, "categoria" TEXT NOT NULL, "link" TEXT NOT NULL, id_loja INTEGER NOT NULL, PRIMARY KEY("id_categoria" AUTOINCREMENT))')
cur.execute('CREATE TABLE "tipos_medida" ("id_medida" INTEGER, "tipo_medida" INTEGER, PRIMARY KEY("id_medida" AUTOINCREMENT))')
cur.execute('CREATE TABLE "precos" ("id_preco" INTEGER, "id_produto" INTEGER NOT NULL, "preco" INTEGER NOT NULL, "data_registo" TEXT NOT NULL, PRIMARY KEY("id_preco" AUTOINCREMENT))')
con.commit()
cur.execute('INSERT INTO lojas VALUES (NULL, "Solmar", "https://res.cloudinary.com/fonte-online/image/upload/c_fill,h_300,q_auto,w_300/v1/PDO_PROD/")')
con.commit()
tiposMedidas = [
  (1, 'Unidade'),
  (2, 'Kg'),
  (3, 'Litro'),
  (4, 'Dose'),
  (5, 'Metro')
]
cur.executemany('INSERT INTO tipos_medida VALUES (?, ?)', tiposMedidas)
con.commit()
con.close()