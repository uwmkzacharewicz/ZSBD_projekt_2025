import oracledb
import bootstrap
import csv
from utils.db_utils import get_connection

def import_investors_from_csv(csv_file):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            with open(csv_file, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    try:
                        cursor.callproc("add_investor", [
                            row['client_code'],
                            row['name'],
                            row['email'],
                            row.get('phone'),
                            row.get('national_id')
                        ])
                        print(f"✅ Dodano inwestora: {row['name']}")
                    # except Exception as e:
                    #     print(f"❌ Błąd dodawania inwestora: {row['name']}")
                    #     print("   Szczegóły:", e)
                    except oracledb.DatabaseError as e:
                        error_obj, = e.args
                        print(f"❌ Błąd dodawania inwestora {row['name']}: {error_obj.message}")

            conn.commit()
            print("✅ Import zakończony.")
    except Exception as e:
        print("❌ Błąd ogólny:", e)


if __name__ == "__main__":
    import_investors_from_csv("data/csv/investors.csv")
