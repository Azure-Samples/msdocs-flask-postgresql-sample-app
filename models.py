from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from app import db

class ImageUpload(db.Model):
    __tablename__ = 'image_upload'
    id = Column(Integer, primary_key=True)

    # Nombre del fichero (sin ruta)
    filename = Column(String(255), nullable=False)

    # Conteo de píxeles según color
    red_pixels   = Column(Integer, nullable=False)
    green_pixels = Column(Integer, nullable=False)
    blue_pixels  = Column(Integer, nullable=False)

    # Fecha y hora de la subida
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Nombre de usuario (alfanumérico libre, puede repetirse)
    user_name   = Column(String(50), nullable=False)

    def __repr__(self):
        return (f"<ImageUpload {self.filename!r} by {self.user_name!r} "
                f"at {self.upload_date:%Y-%m-%d %H:%M:%S}>")
