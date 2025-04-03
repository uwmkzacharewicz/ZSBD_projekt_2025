from flask import Flask
import json, os

def create_app():
    app = Flask(__name__)

    # Załaduj konfigurację
    with open(os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')) as f:
        config = json.load(f)

    app.config.update(config)
    app.secret_key = config.get("FLASK_SECRET_KEY", "fallback-dev-key")

    # Rejestruj blueprinty
    from .routes.home import home_bp
    from .routes.companies import companies_bp
    from .routes.investors import investors_bp
    from .routes.transactions import transactions_bp
    from .routes.stock_prices import stock_prices_bp
    from .routes.portfolio import portfolio_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(companies_bp)
    app.register_blueprint(investors_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(stock_prices_bp)
    app.register_blueprint(portfolio_bp)

    return app
