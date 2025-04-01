import oracledb
import json
import requests
from config.settings import ACTIVE_ENV, CONFIG_FILE, SCHEMA_FILE_URL, SCHEMA_FILE_LOCAL, SCHEMA_SOURCE
import os

def load_config(env):
    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)
    return config[env]


def load_schema():
    if SCHEMA_SOURCE == "github":
        return load_schema_from_github()
    elif SCHEMA_SOURCE == "local":
        return load_schema_from_file()
    else:
        print(f"Nieznane źródło schematu: {SCHEMA_SOURCE}")
        return None


def load_schema_from_github():
    try:
        print(f"Pobieranie schematu z GitHuba: {SCHEMA_FILE_URL}")
        response = requests.get(SCHEMA_FILE_URL)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print("Błąd pobierania pliku SQL z GitHuba:", e)
        return None


def load_schema_from_file():
    try:
        print(f"Wczytywanie lokalnego pliku: {SCHEMA_FILE_LOCAL}")
        with open(SCHEMA_FILE_LOCAL, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print("Błąd wczytywania lokalnego pliku schema.sql:", e)
        return None
    

def execute_schema(sql_text, connection):
    try:
        cursor = connection.cursor()

        # Dzielimy po ';' lub ';\n' dla instrukcji SQL oraz po '/' dla bloków PL/SQL
        blocks = [block.strip() for block in sql_text.split(";") if block.strip()]
        blocks = sum([block.split("\n/") for block in blocks], [])

        print(f"🔄 Wykonywanie {len(blocks)} bloków SQL...")

        for i, block in enumerate(blocks, start=1):
            print(f"🔹 Wykonywanie bloku #{i}:\n{block[:500]}...\n")  # Wyświetl pierwsze 500 znaków bloku
            try:
                # Rozróżnianie bloków PL/SQL
                if block.upper().startswith(("DECLARE", "BEGIN")):
                    print("💡 Wykonanie bloku PL/SQL")
                    cursor.execute(block)
                else:
                    print("💡 Wykonanie zwykłej instrukcji SQL")
                    cursor.execute(block)
            except oracledb.DatabaseError as e:
                error_obj, = e.args
                print(f"⚠️ Błąd w bloku #{i}: {error_obj.message}")
                print(f"⛔ Pominięto fragment:\n{block[:500]}...\n")  # Wyświetl pierwsze 500 znaków z bloku z błędem

        connection.commit()
        print("✅ Skrypt SQL został wykonany.")
    except Exception as e:
        print("❌ Błąd wykonania skryptu SQL:", e)



def run_schema():
    cfg = load_config(ACTIVE_ENV)
    print(f"Połącz z bazą ({ACTIVE_ENV})...")

    try:
        with oracledb.connect(
            user=cfg["user"],
            password=cfg["password"],
            dsn=cfg["dsn"]
        ) as conn:
            print("Połączenie udane.")

            sql_text = load_schema()
            if sql_text:
                execute_schema(sql_text, conn)
    except oracledb.Error as e:
        print("Błąd połączenia:", e)

if __name__ == "__main__":
    print("Rozpoczęcie aktualizacji schematu bazy danych...")
    run_schema()
    print("✅ Aktualizacja schematu bazy danych zakończona.")