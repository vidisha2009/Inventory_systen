import sqlite3
from datetime import datetime

DB_NAME = "inventory.db"

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    # ----------------- SUPPLIERS TABLE -----------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT NOT NULL
        )
    """)

    # ----------------- PRODUCTS TABLE -----------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            supplier_id INTEGER,
            barcode TEXT UNIQUE,
            reorder_level INTEGER DEFAULT 10,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
        )
    """)

    # ----------------- SALES TABLE -----------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity_sold INTEGER NOT NULL,
            sale_date TEXT NOT NULL,
            total_price REAL NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    """)

    # ----------------- TRIGGERS -----------------
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS prevent_negative_quantity
        BEFORE UPDATE ON products
        FOR EACH ROW
        WHEN NEW.quantity < 0
        BEGIN
            SELECT RAISE(ABORT, '❌ Cannot reduce quantity below zero');
        END;
    """)

    conn.commit()
    conn.close()
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database()
