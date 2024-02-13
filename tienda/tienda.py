"""
Módulo tienda
"""

import argparse, yaml,os.path
import sqlite3
from sqlite3 import Error

# leemos los parámetros de entrada
parser = argparse.ArgumentParser()
parser.add_argument('--servidor', dest='servidor', type=str, required=False, default="localhost",help='IP o nombre el servidor donde se inicia la aplicación')
parser.add_argument('--puerto', dest='puerto', type=str, required=False, default='5000',help='puerto donde se expondrá el API')
parser.add_argument('--config', dest='config', type=str, required=True, help='Ruta y nombre del fichero de configuración de la aplicación')
parser.add_argument('--key', dest='key', type=str, required=True, help='Valor del API KEY para consumir servicios de la aplicación almacen')
args = parser.parse_args()

#datos del fichero de config
with open("config.yml", 'r') as ymlfile:     
    cfg = yaml.full_load(ymlfile) 

#debemos tener en cuenta los datos de entrada.
    
existe_bda = os.path.isfile('tienda.db')
if not (existe_bda):
    #no existe la bda, la creamos
    conn = sqlite3.connect('tienda.db')
    c = conn.cursor()
    #creamos la tabla de productos
    c.execute('''
          CREATE TABLE IF NOT EXISTS product
          ([id] INTEGER PRIMARY KEY, [nombre] TEXT, [unidades] INTEGER, [precio] INTEGER )
          ''')
    #se deben obtener dos productos del almacén e insertarlos
    c.execute('''
          INSERT INTO product (id, nombre,unidades,precio)
                VALUES
                (1,'Ordenador',5,400),
                (2,'Impresora',4,100)
          ''')
    conn.commit()
    conn.close
    
#comprobamos los datos, esto es solamente para comprobarlo, habrá que quitar esto
conn = sqlite3.connect('tienda.db')
c = conn.cursor()
c.execute('''
          SELECT
          a.nombre,
          a.precio
          FROM product a
          ''')
rows = c.fetchall()

for row in rows:
    print(row)




#se debe crear un API_KEY para la aplicación tienda.
