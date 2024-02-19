"""
Módulo tienda servicio
"""
import sqlite3
import json
import requests

# variables
path_bda = ""
header = {'api-key': 'a346fef05669ac8eaad0'}
url_api_almacen = ""


def obtener_productos():
    conn = sqlite3.connect(path_bda)
    c = conn.cursor()
    c.execute('''
              Select * from producto
              ''')
    data = c.fetchall()
    conn.close
    return json.dumps(data)


def obtener_producto(id):
    conn = sqlite3.connect(path_bda)
    c = conn.cursor()
    c.execute(
        'Select id,nombre,precio,unidades_vendidas from producto where id=?', (id,))
    data = c.fetchall()
    conn.close
    return json.dumps(data)


def crear_producto(datos_producto):
    conn = sqlite3.connect(path_bda)
    c = conn.cursor()
    c.execute('Insert into producto (id,nombre,precio,unidades_vendidas) values (?,?,?,0)',
              (datos_producto['id'], datos_producto['nombre'], datos_producto['precio']))

    conn.commit()
    conn.close
    return datos_producto['id']


def actualizar_producto(datos_producto):
    conn = sqlite3.connect(path_bda)
    c = conn.cursor()
    c.execute('Update producto set nombre=?,precio=? where id=?',
              (datos_producto['nombre'], datos_producto['precio'], datos_producto['id']))
    conn.commit()
    conn.close
    return datos_producto['id']


def eliminar_producto(id):
    conn = sqlite3.connect(path_bda)
    c = conn.cursor()
    c.execute('Delete from producto where id=?', (id,))
    conn.commit()
    conn.close
    return id


def modificar_precio(id, datos_producto):
    conn = sqlite3.connect(path_bda)
    c = conn.cursor()
    c.execute('Update producto set precio=? where id=?',
              (datos_producto['precio'], id))
    conn.commit()
    conn.close
    return id


def obtener_almacen(id):
    req = requests.get(
        url_api_almacen + "/" + id, headers=header)
    data = req.json()
    respuesta=200
    unidades_disponibles = data['unidades_disponibles']
    if unidades_disponibles > 0:
        # hay unidades, entonces se solicita traspaso del almacén
        req = requests.patch(url_api_almacen + "/" +
                             id + '/registrar-salida', headers=header, json={"cantidad": 1})
        data = req.json()
    else:
        respuesta=600
    return respuesta


def vender_producto(id, cantidad):
    req = requests.get(
        url_api_almacen + "/" + id, headers=header)
    data = req.json()
    retorno=200
    unidades_disponibles = data['unidades_disponibles']
    if unidades_disponibles > cantidad['cantidad']:
        # verificamos que tiene precio
        conn = sqlite3.connect(path_bda)
        c = conn.cursor()
        c.execute('SELECT precio FROM producto where id=?',(id,))
        rows = c.fetchall()
        c.close
        conn.close
        for row in rows:
            precio = (row[0])
        if precio>0:
            # si todo correcto, decrementamos unidades disponibles y aumentamos las vendidas
            conn = sqlite3.connect(path_bda)
            c = conn.cursor()
            c.execute('Update producto set unidades_vendidas=unidades_vendidas+? where id=?',
                  (cantidad['cantidad'], id))
            conn.commit()
            conn.close
        else:
            retorno=601
    else:
        retorno=600
        
    return retorno
