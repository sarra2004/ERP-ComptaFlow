from flask import Blueprint, request, jsonify
from config import db
from models.ecriture_models import Ecriture, JournalComptable, LigneEcriture
from models.account import CompteComptable  # you only IMPORT it

from datetime import datetime

ecriture_bp = Blueprint("ecriture_bp", __name__, url_prefix="/ecritures")

# --------------------------------------------------------
# API 1 : Create an écriture
# --------------------------------------------------------
@ecriture_bp.route("/", methods=["POST"])
def create_ecriture():
    data = request.json

    e = Ecriture(
        date_ecriture=datetime.strptime(data["date_ecriture"], "%Y-%m-%d"),
        libelle=data["libelle"],
        id_journal=data["id_journal"]
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

    db.session.delete(e)
    db.session.commit()

    return jsonify({"message": "Écriture supprimée"})
