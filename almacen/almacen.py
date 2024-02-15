import os
import yaml
import argparse
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from db_models import Base 

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


@app.get('/api/articulos')
def get_articulos():
    return []

@app.get('/api/articulos/<sku>')
def get_articulo(sku: str):
    return ''

@app.post('/api/articulos')
def crear_articulo():
    return ''

@app.put('/api/articulos/<sku>')
def update_articulo():
    return ''

@app.patch('/api/articulos/<sku>/registrar-recepcion')
def registrar_recepcion_articulo(sku: str):
    return ''

@app.patch('/api/articulos/<sku>/registrar-salida')
def registrar_salida_articulo(sku: str):
    return ''


# Levantamos la aplicación
if __name__=="__main__":
    app.run()