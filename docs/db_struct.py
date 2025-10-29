import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

output_file = "db_structure.txt"

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

with open(output_file, "w", encoding="utf-8") as f:
    f.write(f"Database Structure for {DB_NAME}\n")
    f.write("=" * 50 + "\n\n")

    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        f.write(f"Table: {table_name}\n")

        cursor.execute(sql.SQL("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position;
        """), [table_name])
        columns = cursor.fetchall()
        for col in columns:
            f.write(f"   {col[0]} ({col[1]}) {'NULL' if col[2]=='YES' else 'NOT NULL'}\n")

        cursor.execute(sql.SQL("""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = %s AND tc.constraint_type = 'PRIMARY KEY';
        """), [table_name])
        pk = [r[0] for r in cursor.fetchall()]
        if pk:
            f.write(f"   Primary key: {', '.join(pk)}\n")

        cursor.execute(sql.SQL("""
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table,
                ccu.column_name AS foreign_column
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = %s;
        """), [table_name])
        fks = cursor.fetchall()
        if fks:
            f.write("   Foreign keys:\n")
            for fk in fks:
                f.write(f"      {fk[0]} -> {fk[1]}.{fk[2]}\n")

        try:
            cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table_name)))
            count = cursor.fetchone()[0]
            f.write(f"   Rows: {count}\n\n")
        except Exception:
            f.write("   Could not count rows (view or access issue)\n\n")

    f.write("=" * 50 + "\nDone.\n")

cursor.close()
conn.close()
print("Structure saved to", output_file)
