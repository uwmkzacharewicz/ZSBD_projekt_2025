from flask import Blueprint, render_template
from flask import request, redirect, url_for, flash
import yfinance as yf
from utils.db_utils import get_connection
from utils.api_utils import get_actual_currency_rate

stock_prices_bp = Blueprint('stock_prices_bp', __name__, url_prefix="/stock-prices")

@stock_prices_bp.route("/")
def stock_prices():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT company_name, ticker, trade_date, open_price, close_price, close_price_pln, low_price, high_price, volume FROM V_STOCK_PRICES_LATEST")
        data = cursor.fetchall()
    return render_template("stock_prices.html", stock_prices=data)


@stock_prices_bp.route("/import-stock-prices")
def import_stock_prices():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT company_id, ticker FROM Company")
        companies = cursor.fetchall()

        # Pobierz aktualny kurs USD/PLN

        usd_to_pln = get_actual_currency_rate("USD")
        if usd_to_pln is None:
            flash("❌ Nie udało się pobrać kursu USD/PLN", "danger")
            return redirect(url_for("home"))

        print(f"Kurs USD/PLN: {usd_to_pln}")

        for company_id, ticker in companies:
            try:
                data = yf.Ticker(ticker)
                hist = data.history(period="5d")

                for date, row in hist.iterrows():
                    close_usd = float(row['Close'])
                    close_pln = round(close_usd * usd_to_pln, 2)

                    cursor.execute("""
                        INSERT INTO StockPrice (
                            company_id, trade_date, open_price, high_price,
                            low_price, close_price, volume, currency, close_price_pln, source
                        ) VALUES (:1, :2, :3, :4, :5, :6, :7, 'USD', :8, 'yfinance')""",
                        [
                                    company_id,
                                    date.to_pydatetime(),
                                    float(row['Open']),
                                    float(row['High']),
                                    float(row['Low']),
                                    close_usd,
                                    int(row['Volume']),
                                    close_pln
                                    ])

                conn.commit()
                print(f"✅ Dodano dane notowań dla: {ticker}")

            except Exception as e:
                print(f"❌ Błąd przy pobieraniu danych dla {ticker}: {e}")

    flash("✅ Import notowań zakończony", "success")
    return redirect(url_for("home_bp.home")
)

@stock_prices_bp.route("/archive", methods=["GET", "POST"])
def archive_stock_prices():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.callproc("archive_old_prices")
            conn.commit()
        flash("✅ Archiwizacja zakończona sukcesem!", "success")
    except Exception as e:
        flash(f"❌ Błąd archiwizacji: {e}", "danger")

    return redirect(url_for("stock_prices_bp.stock_prices"))
