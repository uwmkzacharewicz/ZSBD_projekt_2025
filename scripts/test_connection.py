import oracledb
import json
from config.settings import ACTIVE_ENV, CONFIG_FILE

def load_config(env):
    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)
    return config[env]

def test_connection():
    cfg = load_config(ACTIVE_ENV)
    try:
        connection = oracledb.connect(
            user=cfg["user"],
            password=cfg["password"],
            dsn=cfg["dsn"]
        )
        print(f"Połączono z bazą ({ACTIVE_ENV}): {connection.version}")

        # Wyświetlanie listy tabel
        cursor = connection.cursor()
        cursor.execute("SELECT table_name FROM user_tables ORDER BY table_name")
        tables = cursor.fetchall()

        if tables:
            print("📋 Istniejące tabele użytkownika:")
            for table in tables:
                print(" -", table[0])
        else:
            print("ℹ️ Brak utworzonych tabel.")
        
        connection.close()
    except oracledb.Error as e:
        print(f"Błąd połączenia ({ACTIVE_ENV}): {e}")

if __name__ == "__main__":
    test_connection()