import requests


def get_actual_currency_rate(currency_code):
    url = f"https://api.nbp.pl/api/exchangerates/rates/a/{currency_code}/?format=json"
    try:
        request = requests.get(url, timeout=10)
        request.raise_for_status()
        data = request.json()
        exchange_rate = data['rates'][0]['mid']
        print(f"Kurs {currency_code}/PLN: {exchange_rate}")
        return exchange_rate
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas pobierania danych z NBP: {e}")
    except KeyError:
        print("Nieoczekiwana struktura odpowiedzi z NBP.")
    return None