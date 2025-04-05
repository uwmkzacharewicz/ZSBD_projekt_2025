from flask import Blueprint, render_template
from flask import request, redirect, url_for, flash
import yfinance as yf
from utils.db_utils import get_connection

transactions_bp = Blueprint('transactions_bp', __name__, url_prefix="/transactions")

@transactions_bp.route("/", methods=["GET", "POST"])
def transaction():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT investor_id, client_code, name FROM Investor ORDER BY name")
        investors = cursor.fetchall()

        cursor.execute("SELECT company_id, name, ticker FROM Company ORDER BY name")
        companies = cursor.fetchall()

    price = None
    final_price = None

    if request.method == "POST":
        investor_id = request.form["investor_id"]
        company_id = request.form["company_id"]
        operation = request.form.get("operation")
        shares = request.form.get("shares")
        commission_rate = float(request.form.get("commission", 5))

        ticker = next(t[2] for t in companies if str(t[0]) == company_id)

        if "get_price" in request.form:
            try:
                data = yf.Ticker(ticker)
                price = data.history(period="1d")["Close"][-1]
                final_price = round(price * (1 + commission_rate / 100), 2)
                flash(f"✅ Cena akcji {ticker}: {price:.2f} USD (z prowizją: {final_price:.2f} USD)", "info")
            except Exception as e:
                flash(f"❌ Błąd pobierania ceny: {e}", "danger")

        elif "submit_transaction" in request.form:
            try:
                data = yf.Ticker(ticker)
                price = data.history(period="1d")["Close"][-1]
                final_price = round(price * (1 + commission_rate / 100), 2)

                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.callproc("make_transaction", [
                        investor_id,
                        company_id,
                        operation,
                        int(shares),
                        float(price),
                        float(commission_rate)
                    ])
                    conn.commit()

                flash("✅ Transakcja została wykonana", "success")
                return redirect(url_for("transactions_bp.transaction"))
            except Exception as e:
                flash(f"❌ Błąd transakcji: {e}", "danger")

    return render_template("transaction.html", investors=investors, companies=companies, price=price, final_price=final_price)