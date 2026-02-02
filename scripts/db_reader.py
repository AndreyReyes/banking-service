#!/usr/bin/env python3
"""
Database reader utility for local inspection.

Usage:
    python scripts/db_reader.py                    # Show all tables with row counts
    python scripts/db_reader.py users              # Show all rows from users table
    python scripts/db_reader.py accounts --limit 5 # Show first 5 rows from accounts
    python scripts/db_reader.py --sql "SELECT * FROM users WHERE id=1"
"""

import argparse
import os
import sqlite3
import sys
from pathlib import Path
from tabulate import tabulate


def get_db_path() -> str:
    """Determine database path from environment or defaults."""
    # Check DATABASE_URL environment variable
    db_url = os.environ.get("DATABASE_URL", "")
    if db_url.startswith("sqlite:///"):
        return db_url.replace("sqlite:///", "").lstrip("./")
    
    # Check common locations
    candidates = [
        "banking.db",
        "data/banking.db",
        "./banking.db",
        "./data/banking.db",
    ]
    for path in candidates:
        if Path(path).exists():
            return path
    
    return "banking.db"  # Default


def connect(db_path: str) -> sqlite3.Connection:
    """Connect to the SQLite database."""
    if not Path(db_path).exists():
        print(f"Error: Database file not found at '{db_path}'")
        print("\nTo create the database, run:")
        print("  python -c 'from app.db.session import run_migrations; run_migrations()'")
        sys.exit(1)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def list_tables(conn: sqlite3.Connection) -> None:
    """List all tables with their row counts."""
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'alembic_%' ORDER BY name"
    )
    tables = [row[0] for row in cursor.fetchall()]
    
    data = []
    for table in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        data.append([table, count])
    
    print("\n📊 Database Tables:")
    print(tabulate(data, headers=["Table", "Rows"], tablefmt="simple"))
    print()


def show_table(conn: sqlite3.Connection, table: str, limit: int | None = None) -> None:
    """Display contents of a table."""
    # Verify table exists
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    )
    if not cursor.fetchone():
        print(f"Error: Table '{table}' not found")
        sys.exit(1)
    
    query = f"SELECT * FROM {table}"
    if limit:
        query += f" LIMIT {limit}"
    
    cursor = conn.execute(query)
    rows = cursor.fetchall()
    
    if not rows:
        print(f"\n📭 Table '{table}' is empty\n")
        return
    
    headers = [desc[0] for desc in cursor.description]
    data = [list(row) for row in rows]
    
    print(f"\n📋 Table: {table}")
    print(tabulate(data, headers=headers, tablefmt="simple"))
    print(f"\n({len(rows)} rows)\n")


def run_sql(conn: sqlite3.Connection, sql: str) -> None:
    """Execute arbitrary SQL and display results."""
    try:
        cursor = conn.execute(sql)
        rows = cursor.fetchall()
        
        if not rows:
            print("\n✅ Query executed (no results)\n")
            return
        
        headers = [desc[0] for desc in cursor.description]
        data = [list(row) for row in rows]
        
        print("\n📋 Query Results:")
        print(tabulate(data, headers=headers, tablefmt="simple"))
        print(f"\n({len(rows)} rows)\n")
    except sqlite3.Error as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Read and inspect the SQLite database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/db_reader.py                     # List all tables
  python scripts/db_reader.py users               # Show users table
  python scripts/db_reader.py accounts -l 10     # Show first 10 accounts
  python scripts/db_reader.py --sql "SELECT * FROM users WHERE id=1"
  python scripts/db_reader.py --db ./data/banking.db users
        """,
    )
    parser.add_argument("table", nargs="?", help="Table name to display")
    parser.add_argument("-l", "--limit", type=int, help="Limit number of rows")
    parser.add_argument("--sql", help="Execute custom SQL query")
    parser.add_argument("--db", help="Path to database file (default: auto-detect)")
    
    args = parser.parse_args()
    
    db_path = args.db or get_db_path()
    print(f"🔗 Database: {db_path}")
    
    conn = connect(db_path)
    
    try:
        if args.sql:
            run_sql(conn, args.sql)
        elif args.table:
            show_table(conn, args.table, args.limit)
        else:
            list_tables(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
