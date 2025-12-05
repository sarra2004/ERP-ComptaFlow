# models/accounting_period.py
from datetime import datetime
from config import db

class AccountingPeriod(db.Model):
    __tablename__ = "accounting_periods"
    
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer)  # NULL pour clôture annuelle
    status = db.Column(db.Enum('OPEN', 'CLOSED', name='period_status'), default='OPEN')
    closing_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('year', 'month', name='unique_period'),
    )
