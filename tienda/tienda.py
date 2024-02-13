"""
Módulo tienda
"""

import argparse, yaml

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


#se debe crear un API_KEY para la aplicación tienda.
