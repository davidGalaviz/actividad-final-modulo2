from sqlalchemy import select
from sqlalchemy.orm import Session
from db_models import Articulo

class ServicioAlmacen:
    def __init__(self, db_engine):
        self.db_engine = db_engine

    def get_articulos(self):
        with Session(self.db_engine) as session:
            query = select(Articulo)

            articulos = []

            for articulo in session.scalars(query):
                articulos.append(articulo.to_json());
            
        return articulos
    
    def get_articulo_por_sku(self, sku: str):
        with Session(self.db_engine) as session:
            query = select(Articulo).where(Articulo.sku == sku)

            articulo = session.scalars(query).first()

        if(articulo is not None):
            return articulo.to_json()
        return None
    
    def crear_articulo(self, articulo):
        with Session(self.db_engine) as session:
            session.add(Articulo(
                sku=articulo['sku'],
                nombre=articulo['nombre'],
                unidades_disponibles=articulo['unidades_disponibles'],
                disponible=articulo['disponible']
            ))

            session.commit()

    def actualizar_articulo(self, sku, datos_articulo):
        with Session(self.db_engine) as session:
            query = select(Articulo).where(Articulo.sku == sku)

            articulo_para_actualizar = session.execute(query).scalar_one()

            # Actualizamos todos los datos del artículo, excepto su SKU
            articulo_para_actualizar.nombre = datos_articulo['nombre']
            articulo_para_actualizar.unidades_disponibles = datos_articulo['unidades_disponibles']
            articulo_para_actualizar.disponible = datos_articulo['disponible']

            session.commit()

    def eliminar_articulo(self, sku):
        with Session(self.db_engine) as session:
            # Localizamos el artículo que queremos eliminar
            articulo_para_eliminar = session.get(Articulo, sku)

            session.delete(articulo_para_eliminar)

            session.commit()


    def registrar_recepcion_articulo(self, sku, cantidad):
        with Session(self.db_engine) as session:
            query = select(Articulo).where(Articulo.sku == sku)

            articulo_para_actualizar = session.execute(query).scalar_one()

            # Incrementamos la cantidad de unidades de disponibles del artículos
            articulo_para_actualizar.unidades_disponibles = articulo_para_actualizar.unidades_disponibles + cantidad

            session.commit()

    def registrar_salida_articulo(self, sku, cantidad):
        with Session(self.db_engine) as session:
            query = select(Articulo).where(Articulo.sku == sku)

            articulo_para_actualizar = session.execute(query).scalar_one()

            # Decrementamos la cantidad de unidades de disponibles del artículos
            articulo_para_actualizar.unidades_disponibles = articulo_para_actualizar.unidades_disponibles - cantidad

            session.commit()


