import os
import sqlite3
os.remove('data/carrinho.sqlite')

con = sqlite3.connect('data/carrinho.sqlite')
cur = con.cursor()

cur.execute('CREATE TABLE "lojas" ("id_loja" INTEGER, "loja" INTEGER UNIQUE, "url_imgs" TEXT, PRIMARY KEY("id_loja" AUTOINCREMENT))')
cur.execute('CREATE TABLE "produtos" ("id_produto" INTEGER, "slug" TEXT NOT NULL UNIQUE, "nome_produto" TEXT NOT NULL, "img" TEXT, "data_registo" TEXT, PRIMARY KEY("id_produto" AUTOINCREMENT))')
cur.execute('CREATE TABLE "tipos_medida" ("id_tipo" INTEGER, "tipo_medida" INTEGER, PRIMARY KEY("id_tipo" AUTOINCREMENT))')
cur.execute('CREATE TABLE "valores" ("id_valor" INTEGER, "id_produto" INTEGER NOT NULL, "id_tipo_medida" INTEGER NOT NULL, "quantidade" INTEGER, "preco" INTEGER NOT NULL, "data_registo" TEXT NOT NULL, PRIMARY KEY("id_valor" AUTOINCREMENT))')
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