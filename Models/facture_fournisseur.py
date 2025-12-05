from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import date
from config import Base

class FactureFournisseur(Base):
    __tablename__ = "factures_fournisseurs"

    id = Column(Integer, primary_key=True, index=True)
    numero_facture = Column(String(100), nullable=False, unique=True)
    date_facture = Column(Date, nullable=False, default=date.today)
    date_echeance = Column(Date)
    montant_ht = Column(Float, nullable=False)
    montant_ttc = Column(Float, nullable=False)
    taxe = Column(Float, default=0)
    etat = Column(String(50), default="EN_ATTENTE")  
    rapprochement_ok = Column(Boolean, default=False)

    fournisseur_id = Column(Integer, ForeignKey("fournisseurs.id"), nullable=False)

    fournisseur = relationship("Fournisseur", back_populates="factures")
    lignes = relationship("LigneFactureFournisseur", back_populates="facture", cascade="all, delete-orphan")
    paiements = relationship("PaiementFournisseur", back_populates="facture")
