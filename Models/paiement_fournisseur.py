from sqlalchemy import Column, Integer, Float, Date, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import date
from config import Base

class PaiementFournisseur(Base):
    __tablename__ = "paiements_fournisseurs"

    id = Column(Integer, primary_key=True)
    date_paiement = Column(Date, default=date.today)
    montant = Column(Float, nullable=False)
    mode_paiement = Column(String(50))  

    facture_id = Column(Integer, ForeignKey("factures_fournisseurs.id"), nullable=False)

    facture = relationship("FactureFournisseur", back_populates="paiements")
