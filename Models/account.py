from datetime import datetime
from config import db

class CompteComptable(db.Model):
    __tablename__ = "compte_comptable"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True, nullable=False)
    intitule = db.Column(db.String(255), nullable=False)
    classe = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50))
    status = db.Column(db.Enum('ACTIVE','INACTIVE', name='status_enum'), default='ACTIVE')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
