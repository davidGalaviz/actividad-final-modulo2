"""
Módulo tienda
"""
import argparse
import yaml
import os.path
import jsonify
import tienda_servicio
import json
import requests
import sqlite3
from flask import Flask, request, jsonify, make_response
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL="/api/docs" # Aquí accederemos al Swagger UI
API_URL="/services/spec" # Aquí servimos los datos del archivo api_doc.yaml

# Leemos los parámetros de entrada
parser = argparse.ArgumentParser(description="""API de Tienda""")
parser.add_argument('--servidor', dest='servidor', type=str, required=False,
                    default="localhost", help='IP o nombre el servidor donde se inicia la aplicación')
parser.add_argument('--puerto', dest='puerto', type=str, required=False,
                    default=5000, help='Puerto donde se expondrá el API')
parser.add_argument('--config', dest='config', type=str, required=True,
                    help='Ruta y nombre del fichero de configuración de la aplicación Tienda')
parser.add_argument('--key', dest='key', type=str, required=True,
                    help='Valor del API KEY para consumir servicios de la aplicación Almacen')
args = parser.parse_args()

path_archivo_config = args.config
nombre_servidor = args.servidor
puerto = args.puerto
api_key_almacen = args.key
header = {'api-key': api_key_almacen}
#se debería poder obtener la url de la api de almacén de un fichero de config
url_api_almacen="http://localhost:3000/api/articulos"
tienda_servicio.url_api_almacen=url_api_almacen

# creamos el fichero cada arranque porque los datos pueden variar
data = {
    'nombre_servidor': nombre_servidor,
    'puerto': puerto,
    'basedatos': {'path': 'tienda.db'}
}
with open(f'{path_archivo_config}', 'w') as f:
    yaml.dump(data, f)

# Obtenemos los datos del fichero de config
with open(path_archivo_config, 'r') as ymlfile:
    cfg = yaml.full_load(ymlfile)

# BDA, si no existe la bda la creamos
path_bda = cfg['basedatos']['path']
tienda_servicio.path_bda = path_bda
existe_bda = os.path.isfile(path_bda)
if not (existe_bda):
    conn = sqlite3.connect(path_bda)
    c = conn.cursor()
    # creamos la tabla de productos
    c.execute('''
          CREATE TABLE IF NOT EXISTS producto
          ([id] TEXT PRIMARY KEY, [nombre] TEXT, [precio] INTEGER, [unidades_vendidas] INTEGER)
          ''')
    # cargamos los productos del almacén. Tiene que estar levantado el api almacén
    req = requests.get(url_api_almacen, headers=header)
    data = req.json()

    for item in data:
        c.execute('Insert into producto (id,nombre,precio,unidades_vendidas) values (?,?,0,0)',
                  (item['sku'], item['nombre'])
                  )
    conn.commit()
    c.close
    conn.close

# comprobamos si hay productos.
conn = sqlite3.connect(path_bda)
c = conn.cursor()
c.execute('''SELECT count(*) FROM producto ''')
rows = c.fetchall()
c.close
conn.close

for row in rows:
    numero_productos = (row[0])

# si no hay productos cargamos dos desde el almacén
if (numero_productos == 0):
    print('No hay productos')

# Inicializamos la aplicación
app = Flask(__name__)
app.config['SERVER_NAME'] = f'{nombre_servidor}:{puerto}'

 # Configuramos Swagger UI (para la documentación)
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'API Tienda'
    }
)

app.register_blueprint(swagger_ui_blueprint)

# Hay que servir la información del archivo api_doc.yaml,
# para que Swagger UI pueda leer la documentación de aquí.
@app.route("/services/spec")
def yaml_docs():
    with open('tienda.yaml', 'r', encoding='utf8') as archivo_docs:
        data = yaml.safe_load(archivo_docs)
        return(data)

@app.get("/api/productos")
def obtener_productos():
    # devolvemos todos los productos
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
    producto = tienda_servicio.crear_producto(datos_producto)

    # ahora obtenemos los datos del producto creado
    response = jsonify(tienda_servicio.obtener_producto(producto))
    response.status_code = 201
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response


@app.put('/api/productos')
def actualizar_producto():
    # Datos producto
    datos_producto = request.get_json()
    producto = tienda_servicio.actualizar_producto(datos_producto)
    # ahora obtenemos los datos del producto creado
    response = jsonify(tienda_servicio.obtener_producto(producto))
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response


@app.delete('/api/productos/<id>')
def eliminar_producto(id: str):
    # Eliminamos el producto con el id
    response = jsonify(tienda_servicio.eliminar_producto(id))
    response = make_response('', 204)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response


@app.put('/api/productos/<id>/modificar-precio')
def modificar_precio(id: str):
    nuevo_precio = request.get_json()
    producto = tienda_servicio.modificar_precio(id, nuevo_precio)
    response = jsonify(tienda_servicio.obtener_producto(producto))
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response


@app.get('/api/productos/<id>/obtener-almacen')
def obtener_almacen(id: str):
    respuesta = tienda_servicio.obtener_almacen(id)
    response = make_response('', respuesta)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response


@app.post('/api/productos/<id>/vender')
def vender_producto(id: str):
    cantidad = request.get_json()
    respuesta = tienda_servicio.vender_producto(id, cantidad)
    #dependiendo de los que nos devuelva , devolvemos una respuesta
    response = make_response('', respuesta)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response


if __name__ == "__main__":
    app.run()
