import csv
from utils.db_utils import get_connection

def import_companies_bulk(csv_file):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            with open(csv_file, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = [
                    (
                        row['name'],
                        row['ticker'],
                        row['sector'],
                        row['country'],
                        row['website']
                    )
                    for row in reader
                ]

            sql = """
                INSERT INTO Company (name, ticker, sector, country, website)
                VALUES (:1, :2, :3, :4, :5)
            """

            cursor.executemany(sql, rows)
            conn.commit()

            print(f"✅ Zaimportowano {len(rows)} firm przez executemany().")

    except Exception as e:
        print("❌ Błąd importu danych:", e)


if __name__ == "__main__":
    import_companies_bulk("data/companies.csv")
