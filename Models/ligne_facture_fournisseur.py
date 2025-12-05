from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from config import Base

class LigneFactureFournisseur(Base):
    __tablename__ = "lignes_facture_fournisseur"

    id = Column(Integer, primary_key=True)
    description = Column(String(255), nullable=False)
    quantite = Column(Float, nullable=False)
    prix_unitaire = Column(Float, nullable=False)
    montant_total = Column(Float, nullable=False)

    compte_charge = Column(String(100), nullable=False)

    facture_id = Column(Integer, ForeignKey("factures_fournisseurs.id"), nullable=False)

    facture = relationship("FactureFournisseur", back_populates="lignes")
