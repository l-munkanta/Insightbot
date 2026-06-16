import sqlite3
import pandas as pd

DB_PATH = "data/business.db"

def run_query(sql: str) -> dict:
    """Execute a SELECT query and return results."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return {
            "success": True,
            "rows": df.head(50).to_dict(orient="records"),
            "columns": list(df.columns),
            "row_count": len(df)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_schema() -> str:
    """Return the database table structure as a string."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    schema_parts = []
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = cursor.fetchall()
        col_defs = ", ".join([f"{c[1]} ({c[2]})" for c in cols])
        schema_parts.append(f"Table: {table} | Columns: {col_defs}")
    conn.close()
    return "\n".join(schema_parts)