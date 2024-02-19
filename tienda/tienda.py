"""
Módulo tienda
"""
import argparse, yaml,os.path,jsonify, tienda_servicio,json,requests,sqlite3
from flask import Flask, request, jsonify
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
api_key_almacen=args.key
header = {'api-key': api_key_almacen}

#Si no existe el fichero de configuración lo creamos con los valores que corresponda
if not (os.path.isfile(fichero_config)):
    data = {
        'servidor': servidor,
        'puerto':puerto,
        'api_key_almacen':api_key_almacen,
        'basedatos': {'path':'tienda.db'}
    }
    with open(f'{fichero_config}','w') as f:
        yaml.dump(data,f)

#Obtenemos los datos del fichero de config
with open(fichero_config, 'r') as ymlfile:     
    cfg = yaml.full_load(ymlfile) 

#BDA, si no existe la bda la creamos
path_bda=cfg['basedatos']['path']
tienda_servicio.path_bda=path_bda
existe_bda = os.path.isfile(path_bda)
if not (existe_bda):
    conn = sqlite3.connect(path_bda)
    c = conn.cursor()
    #creamos la tabla de productos
    c.execute('''
          CREATE TABLE IF NOT EXISTS producto
          ([id] TEXT PRIMARY KEY, [nombre] TEXT, [precio] INTEGER, [unidades_vendidas] INTEGER)
          ''')
    #cargamos los productos del almacén
    req=requests.get('http://localhost:3000/api/articulos',headers=header)
    data=req.json()
    
    for item in data:
         c.execute('Insert into producto (id,nombre,precio,unidades_vendidas) values (?,?,0,0)',
                   (item['sku'],item['nombre'])
                   )
    conn.commit()
    c.close
    conn.close

#comprobamos si hay productos. 
conn = sqlite3.connect(path_bda)
c = conn.cursor()
c.execute('''SELECT count(*) FROM producto ''')
rows = c.fetchall()
c.close
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
    response = jsonify(tienda_servicio.obtener_productos())
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response
    
@app.get('/api/productos/<id>')
def obtener_producto(id: str):
    # Devolvemos el producto con el id 
    response = jsonify(tienda_servicio.obtener_producto(id))
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.post('/api/productos')
def crear_producto():
    # Nuevo producto
    datos_producto = request.get_json()
    producto=tienda_servicio.crear_producto(datos_producto)
    
    #ahora obtenemos los datos del producto creado
    response = jsonify(tienda_servicio.obtener_producto(producto))
    response.status_code = 201
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response
    
@app.put('/api/productos')
def actualizar_producto():
    # Datos producto
    datos_producto = request.get_json()
    producto=tienda_servicio.actualizar_producto(datos_producto)
    #ahora obtenemos los datos del producto creado
    response = jsonify(tienda_servicio.obtener_producto(producto))
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response
    
@app.delete('/api/productos/<id>')
def eliminar_producto(id: str):
    # Eliminamos el producto con el id 
    response = jsonify(tienda_servicio.eliminar_producto(id))
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.put('/api/productos/<id>/modificar-precio')
def modificar_precio(id: str):
    nuevo_precio = request.get_json()
    producto=tienda_servicio.modificar_precio(id,nuevo_precio)
    response = jsonify(tienda_servicio.obtener_producto(producto))
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.get('/api/productos/<id>/obtener-almacen')
def obtener_almacen(id: str):
    response = jsonify(tienda_servicio.obtener_almacen(id))
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.get('/api/productos/<id>/vender')
def vender_producto(id: str):
    cantidad = request.get_json()
    response = jsonify(tienda_servicio.vender_producto(id,cantidad))
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

if __name__=="__main__":
    app.run(host=servidor,port=puerto)
   