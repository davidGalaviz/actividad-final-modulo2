import os
import yaml
import argparse
from flask import Flask, request, jsonify, make_response
from sqlalchemy import create_engine
from flask_swagger_ui import get_swaggerui_blueprint

from db_models import Base 
from servicio_almacen import ServicioAlmacen
from servicio_consumidores import ServicioConsumidores

SWAGGER_URL="/api/docs" # Aquí accederemos al Swagger UI
API_URL="/services/spec" # Aquí servimos los datos del archivo api_doc.yaml

# Recibimos los parámetros ingresados por el usuario
parser = argparse.ArgumentParser(
    description="""API de Almacén"""
)

# Necesitamos el path al archivo de config
parser.add_argument('-config', '--config', type=str,
                    required=True,
                    help="La ruta al archivo config (en formato YAML) de la aplicación.")

# También necesitamos, opcionalmente, el nombre del servidor donde serviremos el API
parser.add_argument('-servidor', '--servidor', type=str,
                    required=False,
                    default='localhost',
                    help="El nombre del servidor donde se servirá el API.")

# También necesitamos, opcionalmente, el puerto donde serviremos el API
parser.add_argument('-puerto', '--puerto', type=str,
                    required=False,
                    default='3000',
                    help="El puerto donde se expondrá el API.")


# Un diccionario que contiene todos los parámetros ingresados por el usuario
args = parser.parse_args()

path_archivo_config = args.config
nombre_servidor = args.servidor
puerto = args.puerto

# Leemos el archivo config
try:
    with open(path_archivo_config, 'r') as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    print(f'Error: No se encontró el archivo config en la ruta {path_archivo_config}')
else:
    # Inicializamos las variables que necesitamos, con los valores que obtuvimos del archivo config
    path_basedatos = config['basedatos']['path']

    # Directorio base, útil para construir paths más adelante
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Inicializamos la aplicación
    app = Flask(__name__)
    # Configuramos el nombre del servidor y el puerto con los valores proveídos por el usuario
    app.config['SERVER_NAME'] = f'{nombre_servidor}:{puerto}'

    # Usando este objeto estableceremos una conexión a la base de datos
    engine = create_engine("sqlite:///" + os.path.join(basedir, path_basedatos), echo=True)

    # Hay que asegurarnos de crear la DB y las tablas correspondientes
    Base.metadata.create_all(engine)

    # Creamos una instancia de nuestro servicio de almacén, la cual nos proveerá métodos
    # para manipular los artículos 
    servicio_almacen = ServicioAlmacen(engine)

    # Creamos una instancia de nuestro servicio de consumidores, la cual nos proveerá métodos
    # para gestionar los consumidores
    servicio_consumidores = ServicioConsumidores(engine)

    # Configuramos Swagger UI (para la documentación)
    swagger_ui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': 'JSON Placeholder/Posts'
        }
    )

    app.register_blueprint(swagger_ui_blueprint)

try:
    # Hay que verificar que haya un consumidor por default en al archivo config
    nombre_consumidor_admin, api_key_consumidor_admin = config['consumidor_almacen'], config['consumidor_almacen_key']

except KeyError:
    # Si no están los datos del consumidor por default, hay que generarlos y guardarlos en el archivo config
    nombre_consumidor_admin = 'admin'
    api_key_consumidor_admin = servicio_consumidores.generar_api_key()

    datos_consumidor_admin = {
        "consumidor_almacen": nombre_consumidor_admin,
        "consumidor_almacen_key": api_key_consumidor_admin
    }

    with open(path_archivo_config, 'a') as file:
        # Nos aseguramos de que los nuevos datos se escriban en una nueva línea
        file.write('\n')
        # Escribimos los datos del consumidor en el archivo config
        yaml.dump(datos_consumidor_admin, file)


# Hay que servir la información del archivo api_doc.yaml,
# para que Swagger UI pueda leer la documentación de aquí.
@app.route("/services/spec")
def yaml_docs():
    with open('api_doc.yaml', 'r',  encoding='utf8') as archivo_docs:
        data = yaml.safe_load(archivo_docs)
        return(data)

def requiere_api_key(func):
    func._requiere_api_key = True
    return func

@app.before_request
def verificar_api_key():
    # Hay varios requests que deben venir acompañados de un API Key válido,
    # bajo el header 'api-key'
    if request.endpoint in app.view_functions:
        view_func = app.view_functions[request.endpoint]
        verificar = hasattr(view_func, '_requiere_api_key')

        if(verificar):
            api_key = request.headers.get('api-key')
            api_key_es_valida = servicio_consumidores.validar_api_key(api_key, api_key_consumidor_admin) if api_key is not None else False

            print(api_key)
            print(api_key_consumidor_admin)
            print(api_key_es_valida)

            # Si el API Key no es válida o no se especificó, devolvemos un error de "Unauthorized"
            if not api_key_es_valida:
                return jsonify({'error': 'Unauthorized'}), 401

@app.post('/api/registrar-consumidor')
def registrar_consumidor():
    # Leemos el nombre del nuevo consumidor que se quiere registrar
    nombre_consumidor = request.get_json()['nombre']

    # Registramos a este nuevo consumidor en la base de datos y le generamos un API Key
    api_key = servicio_consumidores.registrar_consumidor(nombre_consumidor)

    # Le devolvemos al consumidor su API Key, para que la guarde
    # y la pueda usar en sus futuros requests a este API
    response = jsonify({
        "api_key": api_key
    })
    response.status_code = 201
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response


@app.get('/api/articulos')

def get_articulos():
    # Devolvemos la lista completa de artículos
    response = jsonify(servicio_almacen.get_articulos())
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.get('/api/articulos/<sku>')
@requiere_api_key
def get_articulo(sku: str):
    # Devolvemos el artículo con el SKU especificado
    response = jsonify(servicio_almacen.get_articulo_por_sku(sku))
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.post('/api/articulos')
@requiere_api_key
def crear_articulo():
    # Leemos los datos del body del request
    datos_articulo = request.get_json()

    # Guardamos el nuevo artículo en la base de datos
    servicio_almacen.crear_articulo(datos_articulo)

    # Regresamos los datos del artículo creado
    articulo_creado = servicio_almacen.get_articulo_por_sku(datos_articulo['sku'])
    response = jsonify(articulo_creado)
    response.status_code = 201
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.put('/api/articulos/<sku>')
@requiere_api_key
def actualizar_articulo(sku: str):
    # Leemos los datos del body del request
    datos_articulo = request.get_json()

    # Actualizamos el artículo en la base de datos
    servicio_almacen.actualizar_articulo(sku, datos_articulo)

    # Regresamos los datos del artículo actualizado
    articulo_actualizado = servicio_almacen.get_articulo_por_sku(sku)
    response = jsonify(articulo_actualizado)
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.delete('/api/articulos/<sku>')
@requiere_api_key
def eliminar_articulo(sku: str):
    # Eliminamos el artículo de la base de datos
    servicio_almacen.eliminar_articulo(sku)

    # Regresamos una respuesta indicando que se eliminó exitosamente el artículo
    response = make_response('', 204)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.patch('/api/articulos/<sku>/registrar-recepcion')
@requiere_api_key
def registrar_recepcion_articulo(sku: str):
    cantidad = request.get_json()['cantidad']

    # Incrementamos la cantidad de unidades disponibles
    servicio_almacen.registrar_recepcion_articulo(sku, cantidad)

    # Regresamos los datos actualizados del artículo
    articulo_actualizado = servicio_almacen.get_articulo_por_sku(sku)
    response = jsonify(articulo_actualizado)
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.patch('/api/articulos/<sku>/registrar-salida')
@requiere_api_key
def registrar_salida_articulo(sku: str):
    cantidad = request.get_json()['cantidad']

    # Decrementamos la cantidad de unidades disponibles
    servicio_almacen.registrar_salida_articulo(sku, cantidad)

    # Regresamos los datos actualizados del artículo
    articulo_actualizado = servicio_almacen.get_articulo_por_sku(sku)
    response = jsonify(articulo_actualizado)
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response


# Levantamos la aplicación
if __name__=="__main__":
    app.run()