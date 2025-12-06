from flask import Flask
from config import db, Config
from models.accounting_period import AccountingPeriod
from accounting_routes import accounting_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():

        # Import models
        from Models.account import CompteComptable
        from Models.ecritures_models import Ecriture, JournalComptable, LigneEcriture
        # Fournisseurs & Factures
        from Models.fournisseur import Fournisseur
        from Models.facture_fournisseur import FactureFournisseur, LigneFactureFournisseur
        from Models.paiement_fournisseur import PaiementFournisseur

        db.create_all()

    # -----------------------------
    # Register group Blueprints
    # -----------------------------
    from APIs.account_routes import account_bp
    from APIs.ecritures_comptables import ecriture_bp
    from accounting_routes import accounting_bp 
    from APIs.fournisseur_routes import fournisseur_bp
    from APIs.facture_fournisseur_routes import facture_bp

    app.register_blueprint(account_bp)
    app.register_blueprint(ecriture_bp)
    app.register_blueprint(accounting_bp) 
       app.register_blueprint(fournisseur_bp)          
    app.register_blueprint(facture_bp) 

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
