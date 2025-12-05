from flask import Blueprint, request, jsonify
from Models.fournisseur import Fournisseur
from config import db

fournisseur_bp = Blueprint('fournisseur_bp', __name__)

# -------------------------
# 1. Créer un fournisseur
# -------------------------
@fournisseur_bp.route("/fournisseurs", methods=["POST"])
def create_fournisseur():
    data = request.json

    fournisseur = Fournisseur(
        nom=data["nom"],
        email=data.get("email"),
        telephone=data.get("telephone"),
        adresse=data.get("adresse")
    )

    db.session.add(fournisseur)
    db.session.commit()

    return jsonify({"message": "Fournisseur créé", "id": fournisseur.id}), 201


# -------------------------
# 2. Récupérer tous les fournisseurs
# -------------------------
@fournisseur_bp.route("/fournisseurs", methods=["GET"])
def get_all_fournisseurs():
    fournisseurs = Fournisseur.query.all()
    result = [
        {
            "id": f.id,
            "nom": f.nom,
            "email": f.email,
            "telephone": f.telephone,
            "adresse": f.adresse
        }
        for f in fournisseurs
    ]
    return jsonify(result)


# -------------------------
# 3. Récupérer un fournisseur selon son ID
# -------------------------
@fournisseur_bp.route("/fournisseurs/<int:id>", methods=["GET"])
def get_fournisseur(id):
    fournisseur = Fournisseur.query.get_or_404(id)
    return jsonify({
        "id": fournisseur.id,
        "nom": fournisseur.nom,
        "email": fournisseur.email,
        "telephone": fournisseur.telephone,
        "adresse": fournisseur.adresse
    })


# -------------------------
# 4. Mise à jour d'un fournisseur
# -------------------------
@fournisseur_bp.route("/fournisseurs/<int:id>", methods=["PUT"])
def update_fournisseur(id):
    data = request.json
    fournisseur = Fournisseur.query.get_or_404(id)

    fournisseur.nom = data.get("nom", fournisseur.nom)
    fournisseur.email = data.get("email", fournisseur.email)
    fournisseur.telephone = data.get("telephone", fournisseur.telephone)
    fournisseur.adresse = data.get("adresse", fournisseur.adresse)

    db.session.commit()
    return jsonify({"message": "Fournisseur mis à jour"})


# -------------------------
# 5. Suppression d'un fournisseur
# -------------------------
@fournisseur_bp.route("/fournisseurs/<int:id>", methods=["DELETE"])
def delete_fournisseur(id):
    fournisseur = Fournisseur.query.get_or_404(id)
    db.session.delete(fournisseur)
    db.session.commit()
    return jsonify({"message": "Fournisseur supprimé"})
