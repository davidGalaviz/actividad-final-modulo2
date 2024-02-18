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
    c.execute('Select id,nombre,unidades,precio from producto where id=?',(id,))
    data = c.fetchall()
    conn.close
    return json.dumps(data)
    
def crear_producto(datos_producto):
    conn = sqlite3.connect(path_bda)
    c = conn.cursor()
    c.execute('Insert into producto (id,nombre,unidades,precio) values (?,?,?,?)',
              (int(datos_producto['id']),datos_producto['nombre'],datos_producto['unidades'],datos_producto['precio']))
   
    conn.commit()
    conn.close
    
    return datos_producto['id']

def actualizar_producto(datos_producto):
    conn = sqlite3.connect(path_bda)
    c = conn.cursor()
    c.execute('Update producto set nombre=?,unidades=?,precio=? where id=?',(datos_producto['nombre'],datos_producto['unidades'],datos_producto['precio'],datos_producto['id']))
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
