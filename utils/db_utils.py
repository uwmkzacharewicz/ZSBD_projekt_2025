import oracledb
import json
import os
from config.settings import CONFIG_FILE, ACTIVE_ENV

def load_config(env=ACTIVE_ENV):
    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)
    return config.get(env)

# nawiązanie połączenia z bazą danych zgodnie z konfiguracją
def get_connection(env=ACTIVE_ENV):   
    cfg = load_config(env)
    if not cfg:
        raise ValueError(f"Nie znaleziono konfiguracji dla środowiska '{env}'.")

    try:
        conn = oracledb.connect(
            user=cfg["user"],
            password=cfg["password"],
            dsn=cfg["dsn"]
        )
        return conn
    except oracledb.Error as e:
        print(f"Błąd połączenia z bazą danych ({env}): {e}")
        raise
