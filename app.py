from flask import Flask
from config import db, Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialiser SQLAlchemy
    db.init_app(app)

    # Importer les modèles pour qu’ils soient reconnus par SQLAlchemy
    with app.app_context():
        from models.account import CompteComptable
        from models.ecriture_models import Ecriture, JournalComptable, LigneEcriture
        
        db.create_all()  # créer les tables si elles n'existent pas

    # Import and register routes
    from APIs.account_routes import account_bp
    app.register_blueprint(account_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
