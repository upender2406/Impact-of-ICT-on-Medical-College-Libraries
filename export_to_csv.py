import sqlite3
import pandas as pd
import os

DB_PATH = r"backend\database\ict_survey.db"

def export_db_to_csv():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    
    # Get list of tables
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"Found {len(tables)} tables: {[t[0] for t in tables]}")
    
    for table_name in tables:
        table = table_name[0]
        print(f"Exporting table '{table}' to CSV...")
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        csv_filename = f"{table}.csv"
        df.to_csv(csv_filename, index=False)
        print(f"Saved {csv_filename}")
        
    conn.close()

if __name__ == "__main__":
    export_db_to_csv()
