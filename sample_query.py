import psycopg2
from psycopg2 import sql
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

output_dir = "table_samples"
os.makedirs(output_dir, exist_ok=True)

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.autocommit = True
    cursor = conn.cursor()
except Exception as e:
    print("Connection failed", e)
    exit()

cursor.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    ORDER BY table_name;
""")
tables = cursor.fetchall()

for table in tables:
    table_name = table[0]
    query = sql.SQL("SELECT * FROM {} LIMIT 10").format(sql.Identifier(table_name))
    try:
        df = pd.read_sql_query(query.as_string(conn), conn)
        csv_path = os.path.join(output_dir, f"{table_name}_sample.csv")
        df.to_csv(csv_path, index=False)
        print(f"Saved sample from {table_name} to {csv_path}")
    except Exception as e:
        print(f"Could not query table {table_name}:", e)

cursor.close()
conn.close()
print("Done.")
