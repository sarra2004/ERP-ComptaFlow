from flask import Blueprint, request, jsonify
from Models.facture_fournisseur import FactureFournisseur, LigneFactureFournisseur
from Models.fournisseur import Fournisseur
from config import db
from datetime import datetime

facture_bp = Blueprint("facture_bp", __name__)


# -------------------------------------------------------
# 1. CRÉATION FACTURE FOURNISSEUR
# -------------------------------------------------------
@facture_bp.route("/factures", methods=["POST"])
def create_facture():
    data = request.json

    # Vérifier fournisseur
    fournisseur = Fournisseur.query.get(data["fournisseur_id"])
    if not fournisseur:
        return jsonify({"error": "Fournisseur introuvable"}), 404

    facture = FactureFournisseur(
        fournisseur_id=data["fournisseur_id"],
        numero_facture=data["numero_facture"],
        date_facture=datetime.strptime(data["date_facture"], "%Y-%m-%d"),
        date_echeance=datetime.strptime(data["date_echeance"], "%Y-%m-%d")
                       if data.get("date_echeance") else None,
        montant_ht=data["montant_ht"],
        taxe=data["taxe"],
        montant_ttc=data["montant_ttc"],
        etat="SAISIE"
    )

    db.session.add(facture)
    db.session.commit()

    return jsonify({"message": "Facture créée", "id": facture.id}), 201


# -------------------------------------------------------
# 2. AJOUT DES LIGNES FACTURE
# -------------------------------------------------------
@facture_bp.route("/factures/<int:id>/lignes", methods=["POST"])
def add_ligne(id):
    facture = FactureFournisseur.query.get_or_404(id)
    data = request.json

    ligne = LigneFactureFournisseur(
        facture_id=id,
        description=data["description"],
        quantite=data["quantite"],
        prix_unitaire=data["prix_unitaire"],
        tva=data["tva"],
        montant_total=data["quantite"] * data["prix_unitaire"] * (1 + data["tva"])
    )

    db.session.add(ligne)
    db.session.commit()

    return jsonify({"message": "Ligne ajoutée", "ligne_id": ligne.id}), 201


# -------------------------------------------------------
# 3. VALIDATION FACTURE (contrôles automatiques)
# -------------------------------------------------------
@facture_bp.route('/factures/<int:id>/validate', methods=['POST'])
def validate_facture(id):
    facture = FactureFournisseur.query.get_or_404(id)

    # 1. Vérifier qu'il y a des lignes
    if not facture.lignes or len(facture.lignes) == 0:
        return jsonify({"error": "Aucune ligne de facture"}), 400

    # 2. Recalcul automatique du HT et TVA
    total_ht = sum([l.quantite * l.prix_unitaire for l in facture.lignes])
    total_tva = sum([(l.quantite * l.prix_unitaire) * (l.tva / 100) for l in facture.lignes])

    # Mise à jour de la facture
    facture.montant_ht = total_ht
    facture.taxe = total_tva
    facture.montant_ttc = total_ht + total_tva

    # 3. Changer l’état
    facture.etat = "VALIDEE"

    db.session.commit()

    return jsonify({
        "message": "Facture validée avec succès",
        "facture_id": facture.id,
        "montant_ht": facture.montant_ht,
        "montant_tva": facture.taxe,
        "montant_ttc": facture.montant_ttc
    }), 200



# -------------------------------------------------------
# 4. OBTENIR TOUTES LES FACTURES
# -------------------------------------------------------
@facture_bp.route("/factures", methods=["GET"])
def get_factures():
    factures = FactureFournisseur.query.all()
    result = []

    for f in factures:
        result.append({
            "id": f.id,
            "numero_facture": f.numero_facture,
            "fournisseur": f.fournisseur.nom,
            "montant_ht": f.montant_ht,
            "montant_ttc": f.montant_ttc,
            "etat": f.etat,
            "lignes": [
                {
                    "id": l.id,
                    "description": l.description,
                    "quantite": l.quantite,
                    "prix_unitaire": l.prix_unitaire,
                    "montant_total": l.montant_total
                } for l in f.lignes
            ]
        })

    return jsonify(result)


# -------------------------------------------------------
# 5. SUPPRESSION FACTURE (avec lignes en cascade)
# -------------------------------------------------------
@facture_bp.route("/factures/<int:id>", methods=["DELETE"])
def delete_facture(id):
    facture = FactureFournisseur.query.get_or_404(id)

    db.session.delete(facture)
    db.session.commit()

    return jsonify({"message": "Facture supprimée"})
