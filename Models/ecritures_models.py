from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ------------------------
# TABLE 1 : Compte Comptable
# ------------------------
class CompteComptable(db.Model):
    __tablename__ = "compte_comptable"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True, nullable=False)
    intitule = db.Column(db.String(100), nullable=False)
    classe = db.Column(db.String(10), nullable=False)

# ------------------------
# TABLE 2 : Journal Comptable
# ------------------------
class JournalComptable(db.Model):
    __tablename__ = "journal_comptable"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    intitule = db.Column(db.String(100), nullable=False)

# ------------------------
# TABLE 3 : Écriture Comptable
# ------------------------
class Ecriture(db.Model):
    __tablename__ = "ecriture"

    id = db.Column(db.Integer, primary_key=True)
    date_ecriture = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    libelle = db.Column(db.String(200), nullable=False)
    id_journal = db.Column(db.Integer, db.ForeignKey('journal_comptable.id'))

    journal = db.relationship("JournalComptable", backref="ecritures")

# ------------------------
# TABLE 4 : Ligne d'Écriture
# ------------------------
class LigneEcriture(db.Model):
    __tablename__ = "ligne_ecriture"

    id = db.Column(db.Integer, primary_key=True)
    id_ecriture = db.Column(db.Integer, db.ForeignKey('ecriture.id'))
    id_compte = db.Column(db.Integer, db.ForeignKey('compte_comptable.id'))

    debit = db.Column(db.Float, default=0)
    credit = db.Column(db.Float, default=0)

    ecriture = db.relationship("Ecriture", backref="lignes")
    compte = db.relationship("CompteComptable")
