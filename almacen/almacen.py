from flask import Flask

app = Flask(__name__)

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