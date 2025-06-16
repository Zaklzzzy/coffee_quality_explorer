import pathlib
import sqlite3
import pandas as pd

CSV_PATH = pathlib.Path("data/arabica_data_cleaned.csv") 
DB_PATH  = pathlib.Path("coffee.db")

def main() -> None:
    df = pd.read_csv(CSV_PATH)

    df.columns = (
        df.columns
          .str.strip()
          .str.lower()
          .str.replace(r"[ .]", "_", regex=True)
    )

    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql("arabica", conn, if_exists="replace", index=False)
        if "country_of_origin" in df.columns:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_country ON arabica(country_of_origin);")
        print("coffee.db создан / обновлён")

if __name__ == "__main__":
    main()
