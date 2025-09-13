import sqlite3
from db import DB_NAME
from datetime import datetime

# ----------------- PRODUCTS -----------------
def add_product(name, quantity, price, supplier_id=None, barcode=None, reorder_level=10):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, quantity, price, supplier_id, barcode, reorder_level)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, quantity, price, supplier_id, barcode, reorder_level))
    conn.commit()
    conn.close()

def get_all_products():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, quantity, price, supplier_id, barcode, reorder_level
        FROM products
        ORDER BY id ASC
    """)
    products = cursor.fetchall()
    conn.close()
    return products

def get_product_by_barcode(barcode):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, quantity, price, supplier_id, barcode, reorder_level FROM products WHERE barcode=?", (barcode,))
    product = cursor.fetchone()
    conn.close()
    return product

# ----------------- SUPPLIERS -----------------
def add_supplier(name, contact):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO suppliers (name, contact) VALUES (?, ?)", (name, contact))
    conn.commit()
    conn.close()

def get_all_suppliers():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, contact FROM suppliers ORDER BY id ASC")
    suppliers = cursor.fetchall()
    conn.close()
    return suppliers

# ----------------- SALES -----------------
def record_sale(product_id, quantity_sold):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Get product details
    cursor.execute("SELECT quantity, price, reorder_level FROM products WHERE id=?", (product_id,))
    product = cursor.fetchone()
    if not product:
        conn.close()
        raise ValueError("❌ Product not found")
    
    current_qty, price, reorder_level = product
    if quantity_sold > current_qty:
        conn.close()
        raise ValueError("❌ Not enough stock")

    total_price = price * quantity_sold
    sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Record sale
    cursor.execute("""
        INSERT INTO sales (product_id, quantity_sold, sale_date, total_price)
        VALUES (?, ?, ?, ?)
    """, (product_id, quantity_sold, sale_date, total_price))

    # Update product stock
    cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id=?", (quantity_sold, product_id))
    conn.commit()
    conn.close()

    # Return alert if stock below reorder level
    return (current_qty - quantity_sold) < reorder_level

# ----------------- RESET DATABASE -----------------
def reset_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Clear all data
    cursor.execute("DELETE FROM suppliers")
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM sales")

    # Reset AUTOINCREMENT counters for all tables
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='suppliers'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='products'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='sales'")

    conn.commit()
    conn.close()
