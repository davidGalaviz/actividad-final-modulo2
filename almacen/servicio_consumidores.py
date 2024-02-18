import secrets
from sqlalchemy import select
from sqlalchemy.orm import Session
from db_models import Consumidor

class ServicioConsumidores:
    def __init__(self, db_engine):
        self.db_engine = db_engine

    def registrar_consumidor(self, nombre):
        with Session(self.db_engine) as session:
            # Generamos un API Key para este nuevo consumidor
            api_key = self.generar_api_key()
            # Guardamos el consumidor en la base de datos
            session.add(Consumidor(
                nombre=nombre,
                api_key=api_key
            ))

            session.commit()

            # Regresamos el API Key que generamos para este consumidor
            return api_key

    def generar_api_key(self):
        # Generamos un token usando el módulo secrets
        api_key = secrets.token_hex(10)
        return api_key
    
    def validar_api_key(self, api_key_para_verificar, admin_api_key) -> bool:
        # Hay que verificar que el API Key proveído sea o el API key del admin
        # o un API Key de alguno de los consumidores registrados en la base de datos
        if api_key_para_verificar == admin_api_key:
            return True
        else:
            with Session(self.db_engine) as session:
                consumidor_valido = select(Consumidor).where(Consumidor.api_key == api_key_para_verificar)

                if consumidor_valido is not None:
                    return True
                
        return False