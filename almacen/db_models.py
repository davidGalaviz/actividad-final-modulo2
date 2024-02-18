from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

# Todas las clases de los modelos deberán heredar de ésta
class Base(DeclarativeBase):
    pass

class Articulo(Base):
    __tablename__ = "articulos"

    sku: Mapped[str] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column()
    unidades_disponibles: Mapped[int] = mapped_column()
    disponible: Mapped[bool] = mapped_column()

    def __repr__(self) -> str:
        return f"{self.sku}({self.nombre}) - {self.unidades_disponibles} unidades disponibles."
    
    def to_json(self):
        return {
            "sku": self.sku,
            "nombre": self.nombre,
            "unidades_disponibles": self.unidades_disponibles,
            "disponible": True if self.disponible else False
        }

class Consumidor(Base):
    __tablename__ = 'consumidores'

    nombre: Mapped[str] = mapped_column(primary_key=True)
    api_key: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        return f'CONSUMIDOR | Nombre: {self.nombre} | API Key: {self.api_key}'