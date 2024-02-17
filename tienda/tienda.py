"""
Módulo tienda
"""
import argparse, yaml,os.path
import sqlite3
from flask import Flask, request, redirect, Response
from sqlite3 import Error

# leemos los parámetros de entrada
parser = argparse.ArgumentParser()
parser.add_argument('--servidor', dest='servidor', type=str, required=False, default="localhost",help='IP o nombre el servidor donde se inicia la aplicación')
parser.add_argument('--puerto', dest='puerto', type=str, required=False, default=5000,help='Puerto donde se expondrá el API')
parser.add_argument('--config', dest='config', type=str, required=True, help='Ruta y nombre del fichero de configuración de la aplicación Almacén')
parser.add_argument('--key', dest='key', type=str, required=True, help='Valor del API KEY para consumir servicios de la aplicación almacen')
args = parser.parse_args()

#datos de entrada
fichero_config=args.config
servidor=args.servidor #por defecto localhost
puerto=args.puerto #por defecto 5000
key_almacen=args.key

#Si no existe el fichero de configuración lo creamos con los valores que corresponda
if not (os.path.isfile(fichero_config)):
    data = {
        'servidor': servidor,
        'puerto':puerto,
        'key_almacen':key_almacen,
        'basedatos': {'path':'tienda.db'}
    }
    with open(f'{fichero_config}','w') as f:
        yaml.dump(data,f)

#Obtenemos los datos del fichero de config
with open(fichero_config, 'r') as ymlfile:     
    cfg = yaml.full_load(ymlfile) 

#BDA, si no existe la bda la creamos
path_bda=cfg['basedatos']['path']
existe_bda = os.path.isfile(path_bda)
if not (existe_bda):
    conn = sqlite3.connect(path_bda)
    c = conn.cursor()
    #creamos la tabla de productos
    c.execute('''
          CREATE TABLE IF NOT EXISTS producto
          ([id] INTEGER PRIMARY KEY, [nombre] TEXT, [unidades] INTEGER, [precio] INTEGER )
          ''')
    #para pruebas cargamos del inicio tres productos
    #hay que ver como obtener dos productos desde el almacén
    c.execute('''
              Insert into producto values (1,'ordenador',4,700)
              ''')
    c.execute('''
              Insert into producto values (2,'impresora',3,124)
              ''')
    
    c.execute('''
              Insert into producto values (3,'monitor',2,300)
              ''')
    conn.commit()
    conn.close

#comprobamos si hay productos. 
conn = sqlite3.connect(path_bda)
c = conn.cursor()
c.execute('''SELECT count(*) FROM producto ''')
rows = c.fetchall()
conn.close

for row in rows:
    numero_productos=(row[0])

#si no hay productos cargamos dos desde el almacén
if (numero_productos==0):
    print ('No hay productos')
    
# Levantamos la aplicación de tienda
app=Flask (__name__)

@app.get("/api/productos")
def obtener_productos():
    #devolvemos todos los productos
    return Response('productos en json')

@app.get('/api/productos/<id>')
def obtener_producto(id: int):
    # Devolvemos el producto con el id 
    return Response(id)

@app.post('/api/productos')
def crear_producto():
    return Response('creamos el producto:'+id)

@app.put('/api/productos/<id>')
def actualizar_producto(id: int):
    return Response('Actualizmos el producto:'+id)
    
@app.delete('/api/productos/<id>')
def eliminar_producto(id: int):
    return Response('Eliminamos el producto:'+id)

@app.get('/api/productos/<id>/obtener-almacen')
def obtener_almacen(id: int):
    return Response('Obtenemos del almacen:'+id)

@app.get('/api/productos/<id>/modificar-precio')
def modificar_precio(id: int):
    return Response('Modificamos precio')

@app.get('/api/productos/<id>/vender')
def vender_producto(id: int):
    return Response('Vendemos producto')

if __name__=="__main__":
    app.run()
   