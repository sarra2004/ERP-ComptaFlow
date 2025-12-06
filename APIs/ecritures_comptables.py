from flask import Blueprint, request, jsonify
from config import db
from models.ecriture_models import Ecriture, JournalComptable, LigneEcriture
from models.account import CompteComptable  # you only IMPORT it
from datetime import datetime

ecriture_bp = Blueprint("ecriture_bp", __name__, url_prefix="/ecritures")

# --------------------------------------------------------
# FONCTION HELPER : Vérifier si une date est dans une période clôturée
# --------------------------------------------------------
def check_period_open_for_date(date_str):
    """Vérifie si la date est dans une période ouverte"""
    try:
        from models.accounting_period import AccountingPeriod
        
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        year = date.year
        month = date.month
        
        # Vérifier la période mensuelle
        monthly_period = AccountingPeriod.query.filter_by(
            year=year, month=month
        ).first()
        
        if monthly_period and monthly_period.status == 'CLOSED':
            return False, "Impossible : période mensuelle clôturée"
        
        # Vérifier la période annuelle
        annual_period = AccountingPeriod.query.filter_by(
            year=year, month=None
        ).first()
        
        if annual_period and annual_period.status == 'CLOSED':
            return False, "Impossible : période annuelle clôturée"
        
        return True, "Période ouverte"
    except ValueError:
        return False, "Date invalide"

# --------------------------------------------------------
# API 1 : Create an écriture
# --------------------------------------------------------
@ecriture_bp.route("/", methods=["POST"])
def create_ecriture():
    data = request.json

    # MODIFICATION 1 : Vérifier si la période est ouverte
    date_str = data["date_ecriture"]
    is_open, message = check_period_open_for_date(date_str)
    
    if not is_open:
        return jsonify({"error": message}), 403
    
    # MODIFICATION 2 : Ajouter le champ validated=False
    e = Ecriture(
        date_ecriture=datetime.strptime(date_str, "%Y-%m-%d"),
        libelle=data["libelle"],
        id_journal=data["id_journal"],
        validated=False  #  écriture non validée par défaut
    )
    
    db.session.add(e)
    db.session.commit()

    return jsonify({"message": "Écriture créée", "id": e.id})


# --------------------------------------------------------
# API 2 : Add a line to an écriture
# --------------------------------------------------------
@ecriture_bp.route("/<int:id>/lignes", methods=["POST"])
def add_ligne(id):
    data = request.json

    ligne = LigneEcriture(
        id_ecriture=id,
        id_compte=data["id_compte"],
        debit=data.get("debit", 0),
        credit=data.get("credit", 0)
    )

    db.session.add(ligne)
    db.session.commit()

    return jsonify({"message": "Ligne ajoutée"})


# --------------------------------------------------------
# API 3 : List all écritures
# --------------------------------------------------------
@ecriture_bp.route("/", methods=["GET"])
def list_ecritures():
    ecritures = Ecriture.query.all()
    result = []

    for e in ecritures:
        result.append({
            "id": e.id,
            "date": e.date_ecriture.strftime("%Y-%m-%d"),
            "libelle": e.libelle,
            "journal": e.journal.intitule if e.journal else None,
            "validated": e.validated,  # NOUVEAU : inclure l'état de validation
            "lignes": [
                {
                    "compte": l.compte.numero if l.compte else None,
                    "debit": l.debit,
                    "credit": l.credit
                }
                for l in e.lignes
            ]
        })

    return jsonify(result)


# --------------------------------------------------------
# API 4 : Delete an écriture 
# --------------------------------------------------------
@ecriture_bp.route("/<int:id>", methods=["DELETE"])
def delete_ecriture(id):
    e = Ecriture.query.get(id)

    if not e:
        return jsonify({"error": "Écriture non trouvée"}), 404
    
    # MODIFICATION : Vérifier si la période est ouverte
    date_str = e.date_ecriture.strftime("%Y-%m-%d")
    is_open, message = check_period_open_for_date(date_str)
    
    if not is_open:
        return jsonify({"error": message}), 403

    db.session.delete(e)
    db.session.commit()

    return jsonify({"message": "Écriture supprimée"})


# --------------------------------------------------------
# API 5 : Valider une écriture 
# --------------------------------------------------------
@ecriture_bp.route("/<int:id>/validate", methods=["POST"])
def validate_ecriture(id):
    """Valide une écriture après vérification de son équilibre"""
    e = Ecriture.query.get(id)
    
    if not e:
        return jsonify({"error": "Écriture non trouvée"}), 404
    
    # Vérifier l'équilibre débit/crédit
    total_debit = sum(l.debit for l in e.lignes)
    total_credit = sum(l.credit for l in e.lignes)
    
    # Tolérance de 0.01 pour les arrondis
    if abs(total_debit - total_credit) > 0.01:
        return jsonify({
            "error": "Écriture non équilibrée",
            "debit": total_debit,
            "credit": total_credit,
            "difference": total_debit - total_credit
        }), 400
    
    # Marquer l'écriture comme validée
    e.validated = True
    db.session.commit()
    
    return jsonify({
        "message": "Écriture validée avec succès",
        "id": e.id,
        "debit": total_debit,
        "credit": total_credit
    })
# --------------------------------------------------------
# API 5 : Valider une écriture (cloture)
# --------------------------------------------------------
@ecriture_bp.route("/<int:id>/validate", methods=["POST"])
def validate_ecriture(id):
    e = Ecriture.query.get(id)
    
    if not e:
        return jsonify({"error": "Écriture non trouvée"}), 404
    
    # Vérifier l'équilibre débit/crédit
    total_debit = sum(l.debit for l in e.lignes)
    total_credit = sum(l.credit for l in e.lignes)
    
    if abs(total_debit - total_credit) > 0.01:
        return jsonify({
            "error": "Écriture non équilibrée",
            "debit": total_debit,
            "credit": total_credit
        }), 400
    
    e.validated = True
    db.session.commit()
    
    return jsonify({"message": "Écriture validée"})
