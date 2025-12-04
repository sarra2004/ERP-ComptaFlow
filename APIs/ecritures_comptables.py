from flask import Flask, request, jsonify
from models import db, CompteComptable, JournalComptable, Ecriture, LigneEcriture
from datetime import datetime

app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///compta.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# --------------------------
# API 1 : Create an écriture
# --------------------------
@app.route("/ecritures", methods=["POST"])
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

# -------------------------------------------------
# API 2 : Add a line to an écriture (debit/credit)
# -------------------------------------------------
@app.route("/ecritures/<int:id>/lignes", methods=["POST"])
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

# ------------------------------------------
# API 3 : Get all écritures with their lines
# ------------------------------------------
@app.route("/ecritures", methods=["GET"])
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
                    "compte": l.compte.numero,
                    "debit": l.debit,
                    "credit": l.credit
                }
                for l in e.lignes
            ]
        })

    return jsonify(result)

# -------------------------
# API 4 : Delete an écriture
# -------------------------
@app.route("/ecritures/<int:id>", methods=["DELETE"])
def delete_ecriture(id):
    e = Ecriture.query.get(id)

    if not e:
        return jsonify({"error": "Écriture non trouvée"}), 404

    db.session.delete(e)
    db.session.commit()

    return jsonify({"message": "Écriture supprimée"})

# --------------------------
# Launch server
# --------------------------
if __name__ == "__main__":
    app.run(debug=True)
