from flask import Blueprint, render_template
import yfinance as yf
from flask import request, redirect, url_for, flash
from utils.db_utils import get_connection
import os

companies_bp = Blueprint('companies_bp', __name__, url_prefix="/companies")

@companies_bp.route("/")
def companies():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT company_id, name, ticker, sector, country, website FROM Company")
        data = cursor.fetchall()
    return render_template("companies.html", companies=data)

@companies_bp.route("/<int:company_id>")
def company_details(company_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, ticker, sector, country, website FROM Company WHERE company_id = %s", (company_id,))
        company = cursor.fetchone()

        if company:
            cursor.execute("SELECT trade_date, open_price, close_price, low_price, high_price, volume FROM StockPrice WHERE company_id = %s ORDER BY trade_date DESC", (company_id,))
            stock_prices = cursor.fetchall()
        else:
            stock_prices = []

    return render_template("company_details.html", company=company, stock_prices=stock_prices)

@companies_bp.route("/add", methods=["GET", "POST"])
def add_company():
    if request.method == "POST":
        try:
            name = request.form['name']
            ticker = request.form['ticker']
            sector = request.form['sector']
            country = request.form['country']
            website = request.form['website']

            # Sprawdzenie dostępności tickera w yfinance
            try:
                data = yf.Ticker(ticker)
                hist = data.history(period="1d")

                if hist.empty:
                    flash(f"❌ Brak danych historycznych dla tickera '{ticker}' w yfinance!", "danger")
                    return redirect(url_for("add_company"))

            except Exception as e:
                flash(f"❌ Nie można połączyć się z yfinance lub ticker jest nieprawidłowy ({e})", "danger")
                return redirect(url_for("add_company"))

            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.callproc("add_company", [name, ticker, sector, country, website])
                conn.commit()

            flash("✅ Firma została dodana!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"❌ Błąd dodawania firmy: {e}", "danger")
    return render_template("add_company.html")

@companies_bp.route("/delete/<int:company_id>")
def delete_company(company_id):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.callproc("delete_company", [company_id])
            conn.commit()

        flash("✅ Firma została usunięta!", "success")
    except Exception as e:
        flash(f"❌ Błąd usuwania firmy: {e}", "danger")

    return redirect(url_for("companies_bp.companies"))

@companies_bp.route("/import_csv", methods=["GET", "POST"])
def import_companies():
    from scripts.imports.import_companies import import_companies_from_csv

    if request.method == "POST":
        csv_file = request.files.get('csv_file')

        if csv_file and csv_file.filename.endswith('.csv'):
            upload_path = os.path.join("data", "csv", "companies.csv")
            csv_file.save(upload_path)

            try:
                import_companies_from_csv(upload_path)
                flash("✅ Import zakończony pomyślnie!", "success")
            except Exception as e:
                flash(f"❌ Błąd importu: {e}", "danger")
        else:
            flash("❌ Proszę przesłać poprawny plik CSV!", "danger")

        return redirect(url_for("companies_bp.import_companies"))

    return render_template("import_companies.html")

