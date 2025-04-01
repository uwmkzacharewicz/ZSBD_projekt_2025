import requests
import json

from config.settings import CONFIG_FILE

def load_config():
    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)
    return config

config = load_config()

api_key_alpha = config["AlphaVantageAPIkey"]


# Jeśli używasz yfinance:
import yfinance as yf

def test_yfinance_connection(ticker="AAPL"):
    """
    Sprawdza, czy możemy pobrać notowania giełdowe przez bibliotekę yfinance.
    Zwraca True/False w zależności od powodzenia.
    """
    print(f"Test połączenia z yfinance dla ticker: {ticker}")
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="5d")  # Ostatnie 5 dni
        if hist.empty:
            print("Nie pobrano danych (hist jest puste).")
            return False
        else:
            print(f"Pobrano dane. Przykładowy wiersz:\n{hist.head(1)}\n")
            return True
    except Exception as e:
        print("Błąd podczas pobierania danych z yfinance:", e)
        return False

def pobierz_kurs_nbp(kod_waluty):
    """
    Pobiera aktualny kurs średni waluty z API NBP.
    
    Parametry:
    kod_waluty (str): Kod waluty w formacie ISO 4217 (np. 'USD', 'EUR').
    
    Zwraca:
    float: Kurs średni waluty względem PLN lub None w przypadku błędu.
    """
    url = f"https://api.nbp.pl/api/exchangerates/rates/a/{kod_waluty}/?format=json"
    try:
        odpowiedz = requests.get(url, timeout=10)
        odpowiedz.raise_for_status()
        dane = odpowiedz.json()
        kurs = dane['rates'][0]['mid']
        print(f"Kurs {kod_waluty}/PLN: {kurs}")
        return kurs
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas pobierania danych z NBP: {e}")
    except KeyError:
        print("Nieoczekiwana struktura odpowiedzi z NBP.")
    return None

def actual_stock_price():
    """
    Pobiera aktualną cenę akcji z API Alpha Vantage.

    Zwraca:
    float: Aktualna cena akcji lub None w przypadku błędu.
    """
    symbol = 'GOOGL'
    #url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={api_key_alpha}'
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key_alpha}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        price = data["Global Quote"]["05. price"]
        print(f"Aktualna cena akcji {symbol}: {price}")
        return float(price)
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas pobierania danych z Alpha Vantage: {e}")
    except KeyError:
        print("Nieoczekiwana struktura odpowiedzi z Alpha Vantage.")
    return None


def main():
    print("== Test połączenia z zewnętrznymi API ==")
    
    yfinance_ok = test_yfinance_connection("OAI")
    print(f"Wynik testu yfinance: {yfinance_ok}\n")
    pobierz_kurs_nbp('EUR')

    #actual_stock_price()

    # API_KEY = api_key_alpha
    # symbol = 'AAPL'
    # url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}'
    #
    # response = requests.get(url)
    # data = response.json()
    # print(data)


if __name__ == "__main__":   

    main()
