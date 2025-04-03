from flask import Blueprint, render_template
from utils.db_utils import get_connection

portfolio_bp = Blueprint('portfolio_bp', __name__, url_prefix="/portfolio")

@portfolio_bp.route("/")
def portfolio():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT investor_id, investor_name, client_code, company_name, ticker, shares, avg_price
            FROM v_investor_portfolio
            ORDER BY investor_name, company_name
        """)
        data = cursor.fetchall()
    return render_template("portfolio.html", data=data)
