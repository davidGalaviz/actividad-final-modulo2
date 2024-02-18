"""
Módulo tienda servicio
"""
import yaml,os.path,sqlite3,json

path_bda=""

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
    c.execute('Select id,nombre,unidades_vendidas,precio from producto where id=?',(id,))
    data = c.fetchall()
    conn.close
    return json.dumps(data)
    
def crear_producto(datos_producto):
    conn = sqlite3.connect(path_bda)
    c = conn.cursor()
    c.execute('Insert into producto (id,nombre,unidades_vendidas,precio) values (?,?,0,?)',
              (int(datos_producto['id']),datos_producto['nombre'],datos_producto['precio']))
   
    conn.commit()
    conn.close
    return datos_producto['id']

def actualizar_producto(datos_producto):
    conn = sqlite3.connect(path_bda)
    c = conn.cursor()
    c.execute('Update producto set nombre=?,precio=? where id=?',(datos_producto['nombre'],datos_producto['precio'],datos_producto['id']))
    conn.commit()
    conn.close
    
    return datos_producto['id']  

def eliminar_producto(id):
    conn = sqlite3.connect(path_bda)
    c = conn.cursor()
    c.execute('Delete from producto where id=?',(id,))
    conn.commit()
    conn.close
    
    return id

def modificar_precio(id,datos_producto):
    conn = sqlite3.connect(path_bda)
    c = conn.cursor()
    c.execute('Update producto set precio=? where id=?',(datos_producto['precio'],id))
    conn.commit()
    conn.close
    
    return id

def obtener_almacen(id):
     #ira al almacén para saber cuantas unidades hay
    #Si hay suficientes unidades se solicita traspaso (salida de artítulos del almacén)
    #actualizará el producto con la nueva cantidad
    conn = sqlite3.connect(path_bda)
    c = conn.cursor()
    #c.execute('Update producto set precio=? where id=?',(datos_producto['precio'],id))
    conn.commit()
    conn.close
    
    return id

def vender_producto(id):
     #ira al almacén para saber cuantas unidades hay
    #Si hay suficientes unidades se solicita traspaso (salida de artítulos del almacén)
    #actualizará el producto con la nueva cantidad
    conn = sqlite3.connect(path_bda)
    c = conn.cursor()
    #c.execute('Update producto set precio=? where id=?',(datos_producto['precio'],id))
    conn.commit()
    conn.close
    
    return id




