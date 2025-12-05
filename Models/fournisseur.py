from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from config import Base
from datetime import datetime

class Fournisseur(Base):
    __tablename__ = "fournisseurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(200), nullable=False)
    adresse = Column(String(255))
    email = Column(String(120))
    telephone = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    factures = relationship("FactureFournisseur", back_populates="fournisseur")
