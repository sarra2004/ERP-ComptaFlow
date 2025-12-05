# accounting_routes.py
from flask import Blueprint, request, jsonify
from config import db
from datetime import datetime
from models.accounting_period import AccountingPeriod
from models.ecriture_models import Ecriture, LigneEcriture
from models.account import CompteComptable
from sqlalchemy import func, and_, or_

accounting_bp = Blueprint("accounting_bp", __name__, url_prefix="/accounting")

# --------------------------------------------------------
# Helper: Vérifier si une période est clôturée
# --------------------------------------------------------
def is_period_closed(year, month=None):
    """Vérifie si une période est clôturée"""
    query = AccountingPeriod.query.filter_by(year=year)
    if month:
        query = query.filter_by(month=month)
    else:
        query = query.filter_by(month=None)  # Période annuelle
    
    period = query.first()
    return period.status == 'CLOSED' if period else False

# --------------------------------------------------------
# Middleware: Vérifier les écritures avant modification
# --------------------------------------------------------
def check_period_open_for_date(date_str):
    """Vérifie si la date est dans une période ouverte"""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        year = date.year
        month = date.month
        
        # Vérifier la période mensuelle
        monthly_period = AccountingPeriod.query.filter_by(
            year=year, month=month
        ).first()
        
        if monthly_period and monthly_period.status == 'CLOSED':
            return False, "Période mensuelle clôturée"
        
        # Vérifier la période annuelle
        annual_period = AccountingPeriod.query.filter_by(
            year=year, month=None
        ).first()
        
        if annual_period and annual_period.status == 'CLOSED':
            return False, "Période annuelle clôturée"
        
        return True, "Période ouverte"
    except ValueError:
        return False, "Date invalide"

# --------------------------------------------------------
# API 1 : Clôturer une période
# --------------------------------------------------------
@accounting_bp.route("/close", methods=["POST"])
def close_period():
    data = request.json
    
    # Validation des données
    if "year" not in data:
        return jsonify({"error": "L'année est requise"}), 400
    
    year = data["year"]
    month = data.get("month")  # Optionnel pour clôture annuelle
    
    # Étape 1: Vérifier/créer la période
    period = AccountingPeriod.query.filter_by(year=year, month=month).first()
    if not period:
        period = AccountingPeriod(year=year, month=month, status='OPEN')
        db.session.add(period)
        db.session.commit()
    
    if period.status == 'CLOSED':
        return jsonify({"error": "Période déjà clôturée"}), 400
    
    # Étape 2: Vérifier les écritures non validées
    if month:
        # Clôture mensuelle
        non_validated = Ecriture.query.filter(
            db.extract('year', Ecriture.date_ecriture) == year,
            db.extract('month', Ecriture.date_ecriture) == month,
            Ecriture.validated == False
        ).count()
    else:
        # Clôture annuelle
        non_validated = Ecriture.query.filter(
            db.extract('year', Ecriture.date_ecriture) == year,
            Ecriture.validated == False
        ).count()
    
    if non_validated > 0:
        return jsonify({
            "error": f"{non_validated} écriture(s) non validée(s)",
            "message": "Veuillez valider toutes les écritures avant la clôture"
        }), 400
    
    # Étape 3: Vérifier l'équilibre des journaux
    # Pour chaque écriture, vérifier que débit = crédit
    if month:
        ecritures = Ecriture.query.filter(
            db.extract('year', Ecriture.date_ecriture) == year,
            db.extract('month', Ecriture.date_ecriture) == month
        ).all()
    else:
        ecritures = Ecriture.query.filter(
            db.extract('year', Ecriture.date_ecriture) == year
        ).all()
    
    for ecriture in ecritures:
        total_debit = sum(l.debit for l in ecriture.lignes)
        total_credit = sum(l.credit for l in ecriture.lignes)
        
        if abs(total_debit - total_credit) > 0.01:  # Tolérance pour les arrondis
            return jsonify({
                "error": f"Écriture {ecriture.id} non équilibrée",
                "message": f"Débit: {total_debit}, Crédit: {total_credit}"
            }), 400
    
    # Étape 4: Calculer les soldes des comptes (pour clôture annuelle)
    if not month:  # Clôture annuelle
        # Calculer les soldes de tous les comptes
        from sqlalchemy import text
        
        query = text("""
            SELECT 
                c.id as compte_id,
                c.numero,
                c.intitule,
                COALESCE(SUM(l.debit), 0) as total_debit,
                COALESCE(SUM(l.credit), 0) as total_credit,
                COALESCE(SUM(l.debit), 0) - COALESCE(SUM(l.credit), 0) as solde
            FROM compte_comptable c
            LEFT JOIN ligne_ecriture l ON c.id = l.id_compte
            LEFT JOIN ecriture e ON l.id_ecriture = e.id
            WHERE EXTRACT(YEAR FROM e.date_ecriture) = :year
            GROUP BY c.id, c.numero, c.intitule
            HAVING COALESCE(SUM(l.debit), 0) != 0 OR COALESCE(SUM(l.credit), 0) != 0
        """)
        
        result = db.session.execute(query, {'year': year})
        soldes = []
        
        for row in result:
            soldes.append({
                "compte_id": row.compte_id,
                "numero": row.numero,
                "intitule": row.intitule,
                "solde": row.solde
            })
        
        # Vous pourriez ici générer les écritures d'à-nouveaux
        # et les insérer dans la base de données
    
    # Étape 5: Marquer la période comme clôturée
    period.status = 'CLOSED'
    period.closing_date = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        "message": "Période clôturée avec succès",
        "period_id": period.id,
        "year": year,
        "month": month,
        "closing_date": period.closing_date.strftime("%Y-%m-%d %H:%M:%S")
    }), 200

# --------------------------------------------------------
# API 2 : Voir les périodes
# --------------------------------------------------------
@accounting_bp.route("/periods", methods=["GET"])
def list_periods():
    periods = AccountingPeriod.query.order_by(
        AccountingPeriod.year.desc(),
        AccountingPeriod.month.desc()
    ).all()
    
    result = []
    for p in periods:
        result.append({
            "id": p.id,
            "year": p.year,
            "month": p.month,
            "status": p.status,
            "closing_date": p.closing_date.strftime("%Y-%m-%d %H:%M") if p.closing_date else None,
            "created_at": p.created_at.strftime("%Y-%m-%d")
        })
    
    return jsonify(result)

# --------------------------------------------------------
# API 3 : Réouvrir une période 
# --------------------------------------------------------
@accounting_bp.route("/<int:id>/reopen", methods=["POST"])
def reopen_period(id):
    period = AccountingPeriod.query.get(id)
    
    if not period:
        return jsonify({"error": "Période non trouvée"}), 404
    
    if period.status != 'CLOSED':
        return jsonify({"error": "La période n'est pas clôturée"}), 400
    
    # Vérifier s'il existe des périodes plus récentes clôturées
    # (pour éviter de réouvrir une période intermédiaire)
    if period.month:
        newer_closed = AccountingPeriod.query.filter(
            AccountingPeriod.year == period.year,
            AccountingPeriod.month > period.month,
            AccountingPeriod.status == 'CLOSED'
        ).first()
    else:
        # Pour les périodes annuelles
        newer_closed = AccountingPeriod.query.filter(
            AccountingPeriod.year > period.year,
            AccountingPeriod.status == 'CLOSED'
        ).first()
    
    if newer_closed:
        return jsonify({
            "error": "Impossible de réouvrir: périodes plus récentes clôturées"
        }), 403
    
    period.status = 'OPEN'
    period.closing_date = None
    db.session.commit()
    
    return jsonify({"message": "Période réouverte avec succès"})

# --------------------------------------------------------
# API 4 : Générer le bilan
# --------------------------------------------------------
@accounting_bp.route("/bilan/<int:year>", methods=["GET"])
def generate_bilan(year):
    """Génère le bilan pour une année donnée"""
    
    # Vérifier si l'année est clôturée
    period = AccountingPeriod.query.filter_by(year=year, month=None).first()
    if not period or period.status != 'CLOSED':
        return jsonify({
            "error": "L'année doit être clôturée pour générer le bilan"
        }), 400
    
    # Calculer les totaux par classe de comptes
    query = """
        SELECT 
            c.classe,
            SUM(l.debit) as total_debit,
            SUM(l.credit) as total_credit,
            SUM(l.debit - l.credit) as solde
        FROM compte_comptable c
        LEFT JOIN ligne_ecriture l ON c.id = l.id_compte
        LEFT JOIN ecriture e ON l.id_ecriture = e.id
        WHERE EXTRACT(YEAR FROM e.date_ecriture) = :year
        GROUP BY c.classe
        ORDER BY c.classe
    """
    
    result = db.session.execute(query, {'year': year})
    
    bilan = {
        "year": year,
        "actif": [],  # Classes 1-5
        "passif": [],  # Classes 6-8
        "total_actif": 0,
        "total_passif": 0
    }
    
    for row in result:
        classe_data = {
            "classe": row.classe,
            "total_debit": float(row.total_debit or 0),
            "total_credit": float(row.total_credit or 0),
            "solde": float(row.solde or 0)
        }
        
        if row.classe <= 5:
            bilan["actif"].append(classe_data)
            bilan["total_actif"] += abs(float(row.solde or 0))
        else:
            bilan["passif"].append(classe_data)
            bilan["total_passif"] += abs(float(row.solde or 0))
    
    return jsonify(bilan)
