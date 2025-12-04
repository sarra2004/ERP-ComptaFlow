# models/ecriture_models.py

from config import db
from datetime import datetime

# ------------------------
# TABLE 1 : Journal Comptable
# ------------------------
class JournalComptable(db.Model):
    __tablename__ = "journal_comptable"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    intitule = db.Column(db.String(100), nullable=False)


# ------------------------
# TABLE 2 : Écriture Comptable
# ------------------------
class Ecriture(db.Model):
    __tablename__ = "ecriture"

    id = db.Column(db.Integer, primary_key=True)
    date_ecriture = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    libelle = db.Column(db.String(200), nullable=False)

    id_journal = db.Column(db.Integer, db.ForeignKey('journal_comptable.id'))
    journal = db.relationship("JournalComptable", backref="ecritures")


# ------------------------
# TABLE 3 : Ligne d'Écriture
# ------------------------
class LigneEcriture(db.Model):
    __tablename__ = "ligne_ecriture"

    id = db.Column(db.Integer, primary_key=True)
    id_ecriture = db.Column(db.Integer, db.ForeignKey('ecriture.id'))
    id_compte = db.Column(db.Integer, db.ForeignKey('compte_comptable.id'))  # from your friend's model

    debit = db.Column(db.Float, default=0)
    credit = db.Column(db.Float, default=0)

    ecriture = db.relationship("Ecriture", backref="lignes")
