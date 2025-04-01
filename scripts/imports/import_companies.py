import oracledb
import bootstrap
import csv
from utils.db_utils import get_connection

def import_companies_from_csv(csv_file):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            with open(csv_file, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    try:
                        cursor.callproc("add_company", [
                            row['name'],
                            row['ticker'],
                            row['sector'],
                            row['country'],
                            row['website']
                        ])
                        print(f"✅ Dodano firmę: {row['name']}")
                    except Exception as e:
                        print(f"❌ Błąd dodawania firmy: {row['name']}")
                        print("   Szczegóły:", e)

            conn.commit()

    except Exception as e:
        print("❌ Błąd główny (połączenie lub plik CSV):", e)


if __name__ == "__main__":
    import_companies_from_csv("data/csv/companies.csv")
