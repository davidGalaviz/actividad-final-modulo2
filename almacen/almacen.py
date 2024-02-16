import os
import yaml
import argparse
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from db_models import Base 
from servicio_almacen import ServicioAlmacen

# Recibimos los parámetros ingresados por el usuario
parser = argparse.ArgumentParser(
    description="""API de Almacén"""
)

# Necesitamos el path al archivo de config
parser.add_argument('-config', '--config', type=str,
                    required=True,
                    help="La ruta al archivo config (en formato YAML) de la aplicación.")

# Un diccionario que contiene todos los parámetros ingresados por el usuario
args = parser.parse_args()

path_archivo_config = args.config

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

    # Inicializamos la aplicación con los datos del archivo config
    app = Flask(__name__)

    # Usando este objeto estableceremos una conexión a la base de datos
    engine = create_engine("sqlite:///" + os.path.join(basedir, path_basedatos), echo=True)

    # Hay que asegurarnos de crear la DB y las tablas correspondientes
    Base.metadata.create_all(engine)

    # Creamos una instancia de nuestro servicio, la cual nos proveerá métodos
    # para manipular los artículos 
    servicio = ServicioAlmacen(engine)


@app.get('/api/articulos')
def get_articulos():
    # Devolvemos la lista completa de artículos
    return servicio.get_articulos()

@app.get('/api/articulos/<sku>')
def get_articulo(sku: str):
    # Devolvemos el artículo con el SKU especificado
    return servicio.get_articulo_por_sku(sku)

@app.post('/api/articulos')
def crear_articulo():
    # Leemos los datos del body del request
    datos_articulo = request.get_json()

    # Guardamos el nuevo artículo en la base de datos
    servicio.crear_articulo(datos_articulo)

    # Regresamos los datos del artículo creado
    articulo_creado = servicio.get_articulo_por_sku(datos_articulo['sku'])
    return articulo_creado

@app.put('/api/articulos/<sku>')
def actualizar_articulo(sku: str):
    # Leemos los datos del body del request
    datos_articulo = request.get_json()

    # Actualizamos el artículo en la base de datos
    servicio.actualizar_articulo(sku, datos_articulo)

    # Regresamos los datos del artículo actualizado
    articulo_actualizado = servicio.get_articulo_por_sku(sku)
    return articulo_actualizado

@app.patch('/api/articulos/<sku>/registrar-recepcion')
def registrar_recepcion_articulo(sku: str):
    return ''

@app.patch('/api/articulos/<sku>/registrar-salida')
def registrar_salida_articulo(sku: str):
    return ''


# Levantamos la aplicación
if __name__=="__main__":
    app.run()