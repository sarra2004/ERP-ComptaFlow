from flask import Blueprint, request, jsonify
from models.account import CompteComptable
from config import db

account_bp = Blueprint("account_bp", __name__)


# ---------------------------------------------
# Helper : vérifier si un compte est utilisé 
# (Placeholder, toujours False pour toi)
# ---------------------------------------------
def account_is_used(account_id):
    return False


# -------------------------------------------------
# API 1 : CREATE ACCOUNT (POST /accounts)
# -------------------------------------------------
@account_bp.route("/accounts", methods=["POST"])
def create_account():
    data = request.json

    required_fields = ["number", "label", "class", "type"]
    for f in required_fields:
        if f not in data:
            return jsonify({"error": f"Field '{f}' is required"}), 400

    if not data["label"].strip():
        return jsonify({"error": "Label cannot be empty"}), 400

    if not str(data["class"]).isdigit() or not (1 <= int(data["class"]) <= 8):
        return jsonify({"error": "Class must be between 1 and 8"}), 400

    if Account.query.filter_by(number=data["number"]).first():
        return jsonify({"error": "Account number already exists"}), 409

    acc = Account(
        number=data["number"],
        label=data["label"],
        class_number=int(data["class"]),
        type=data["type"],
    )

    db.session.add(acc)
    db.session.commit()

    return jsonify({"message": "Account created", "id": acc.id}), 201


# -------------------------------------------------
# API 2 : UPDATE ACCOUNT
# -------------------------------------------------
@account_bp.route("/accounts/<int:id>", methods=["PUT"])
def update_account(id):
    data = request.json
    acc = Account.query.get(id)

    if not acc:
        return jsonify({"error": "Account not found"}), 404

    if "number" in data and data["number"] != acc.number:
        if Account.query.filter_by(number=data["number"]).first():
            return jsonify({"error": "New account number already exists"}), 409
        acc.number = data["number"]

    if "label" in data:
        if not data["label"].strip():
            return jsonify({"error": "Label cannot be empty"}), 400
        acc.label = data["label"]

    if "class" in data:
        if not str(data["class"]).isdigit() or not (1 <= int(data["class"]) <= 8):
            return jsonify({"error": "Class must be between 1 and 8"}), 400
        acc.class_number = int(data["class"])

    if "type" in data:
        acc.type = data["type"]

    db.session.commit()

    return jsonify({"message": "Account updated"})


# -------------------------------------------------
# API 3 : DISABLE ACCOUNT
# -------------------------------------------------
@account_bp.route("/accounts/<int:id>/disable", methods=["PATCH"])
def disable_account(id):
    acc = Account.query.get(id)

    if not acc:
        return jsonify({"error": "Account not found"}), 404

    acc.status = "INACTIVE"
    db.session.commit()

    return jsonify({"message": "Account disabled"}), 200


# -------------------------------------------------
# API 4 : DELETE ACCOUNT
# -------------------------------------------------
@account_bp.route("/accounts/<int:id>", methods=["DELETE"])
def delete_account(id):
    acc = Account.query.get(id)

    if not acc:
        return jsonify({"error": "Account not found"}), 404

    if account_is_used(id):
        return jsonify({
            "error": "Cannot delete an account with linked entries"
        }), 403

    db.session.delete(acc)
    db.session.commit()

    return jsonify({"message": "Account deleted"})


# -------------------------------------------------
# API 5 : GET ACCOUNTS
# -------------------------------------------------
@account_bp.route("/accounts", methods=["GET"])
def list_accounts():
    query = Account.query

    classe = request.args.get("class")
    type_ = request.args.get("type")
    status = request.args.get("status")

    if classe:
        query = query.filter_by(class_number=int(classe))
    if type_:
        query = query.filter_by(type=type_)
    if status:
        query = query.filter_by(status=status.upper())

    accounts = query.all()

    result = [
        {
            "id": a.id,
            "number": a.number,
            "label": a.label,
            "class": a.class_number,
            "type": a.type,
            "status": a.status,
            "created_at": a.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for a in accounts
    ]

    return jsonify(result)
