from config import db

class FactureFournisseur(db.Model):
    __tablename__ = "factures_fournisseur"

    id = db.Column(db.Integer, primary_key=True)
    fournisseur_id = db.Column(db.Integer, db.ForeignKey("fournisseurs.id"))
    invoice_number = db.Column(db.String(100))
    date_facture = db.Column(db.Date)
    date_echeance = db.Column(db.Date)
    total_ht = db.Column(db.Numeric)
    total_tva = db.Column(db.Numeric)
    total_ttc = db.Column(db.Numeric)
    statut = db.Column(db.String(50), default="DRAFT")

    lignes = db.relationship("LigneFactureFournisseur", backref="facture", lazy=True)
