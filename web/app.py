from flask import Flask, render_template, request, redirect, url_for, flash
import oracledb
import json
import os
import yfinance as yf
from datetime import datetime


with open(os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')) as f:
    config = json.load(f)

env = "local"
cfg = config[env]

app = Flask(__name__)
app.secret_key = config.get("FLASK_SECRET_KEY")
if config.get("FLASK_SECRET_KEY") is None:
    raise RuntimeError("Brak FLASK_SECRET_KEY w config.json!")

def get_connection():
    return oracledb.connect(
        user=cfg["user"],
        password=cfg["password"],
        dsn=cfg["dsn"]
    )

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/investors")
def investors():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Investor")
        investors = cursor.fetchall()
    return render_template("investors.html", investors=investors)
@app.route("/companies")
def index():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT company_id, name, ticker, sector, country, website FROM Company")
        companies = cursor.fetchall()
    return render_template("companies.html", companies=companies)

@app.route("/add", methods=["GET", "POST"])
def add_company():
    if request.method == "POST":
        try:
            name = request.form['name']
            ticker = request.form['ticker']
            sector = request.form['sector']
            country = request.form['country']
            website = request.form['website']

            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.callproc("add_company", [name, ticker, sector, country, website])
                conn.commit()

            flash("✅ Firma została dodana!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"❌ Błąd dodawania firmy: {e}", "danger")
    return render_template("add_company.html")



@app.route("/transaction", methods=["GET", "POST"])
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
                return redirect(url_for("transaction"))
            except Exception as e:
                flash(f"❌ Błąd transakcji: {e}", "danger")

    return render_template("transaction.html", investors=investors, companies=companies, price=price, final_price=final_price)



@app.route("/import_stock_prices")
def import_stock_prices():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT company_id, ticker FROM Company")
        companies = cursor.fetchall()

        for company_id, ticker in companies:
            try:
                data = yf.Ticker(ticker)
                hist = data.history(period="5d")

                for date, row in hist.iterrows():
                    cursor.execute("""
                        INSERT INTO StockPrice (
                            company_id, trade_date, open_price, high_price,
                            low_price, close_price, volume, currency, close_price_pln, source
                        ) VALUES (:1, :2, :3, :4, :5, :6, :7, 'USD', NULL, 'yfinance')""", [
                        company_id,
                        date.to_pydatetime(),
                        float(row['Open']),
                        float(row['High']),
                        float(row['Low']),
                        float(row['Close']),
                        int(row['Volume'])
                    ])

                conn.commit()
                print(f"✅ Dodano dane notowań dla: {ticker}")

            except Exception as e:
                print(f"❌ Błąd przy pobieraniu danych dla {ticker}: {e}")

    flash("✅ Import notowań zakończony", "success")
    return redirect(url_for("index"))

@app.route("/portfolio")
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


if __name__ == "__main__":
    app.run(debug=True)
