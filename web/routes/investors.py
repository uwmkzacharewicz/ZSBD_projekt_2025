from flask import Blueprint, render_template
from utils.db_utils import get_connection

investors_bp = Blueprint('investors_bp', __name__, url_prefix="/investors")

@investors_bp.route("/")
def investors():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT investor_id, client_code, name, email, phone, national_id, created_at FROM Investor")
        data = cursor.fetchall()
    return render_template("investors.html", investors=data)
