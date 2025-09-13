import tkinter as tk
from tkinter import messagebox, ttk
from db import setup_database, DB_NAME
from services import (
    add_product, get_all_products, record_sale,
    add_supplier, get_all_suppliers, reset_database,
    get_product_by_barcode
)
import sqlite3

# ✅ New imports for analytics
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ----------------- MAIN WINDOW -----------------
root = tk.Tk()
root.title("Inventory Management System")
root.geometry("1100x700")
root.config(bg="white")

setup_database()

# ----------------- HEADER -----------------
header = tk.Frame(root, bg="#0d1f4a", height=70)
header.pack(fill="x")

title = tk.Label(
    header,
    text="Inventory Management System",
    bg="#0d1f4a",
    fg="white",
    font=("Segoe UI", 22, "bold")
)
title.pack(pady=15)

# ----------------- SIDEBAR -----------------
sidebar = tk.Canvas(root, width=230, height=700, bd=0, highlightthickness=0)
sidebar.pack(fill="y", side="left")
sidebar.create_rectangle(0, 0, 230, 700, fill="#0d1f4a", outline="")

button_frame = tk.Frame(sidebar, bg="#0d1f4a")
button_frame.place(x=0, y=50)

def create_sidebar_button(text, command, color="white"):
    return tk.Button(
        button_frame, text=text, command=command,
        bg="#0d1f4a", fg=color,
        activebackground="#0d1f4a", activeforeground=color,
        font=("Segoe UI", 12, "bold"),
        bd=0, relief="flat", highlightthickness=0, anchor="w", padx=20
    )

# ----------------- MAIN CONTENT -----------------
content = tk.Frame(root, bg="white")
content.pack(fill="both", expand=True, side="right")

table_frame = tk.Frame(content, bg="white")
table_frame.pack(fill="both", expand=True, padx=20, pady=20)

tree = ttk.Treeview(table_frame, show="headings", height=20)
tree.pack(fill="both", expand=True)

# ----------------- TREEVIEW STYLE -----------------
style = ttk.Style()
style.configure("Treeview",
                font=("Segoe UI", 11),
                rowheight=32,
                background="white",
                fieldbackground="white")
style.configure("Treeview.Heading",
                font=("Segoe UI", 12, "bold"),
                background="white",
                foreground="#0d1f4a")
style.map("Treeview", background=[("selected", "#f0f0f0")])

# ----------------- FUNCTIONS -----------------
def show_products():
    for row in tree.get_children():
        tree.delete(row)
    tree["columns"] = ("ID", "Name", "Quantity", "Price", "Supplier", "Barcode", "Reorder Level")
    for col in tree["columns"]:
        tree.heading(col, text=col, anchor="center")
        tree.column(col, anchor="center", width=120)

    tree.tag_configure('low_stock', background='#f8d7da')

    for pid, name, qty, price, supplier_id, barcode, reorder_level in get_all_products():
        supplier_name = ""
        if supplier_id:
            suppliers = get_all_suppliers()
            supplier_dict = {s[0]: s[1] for s in suppliers}
            supplier_name = supplier_dict.get(supplier_id, "")
        tag = 'low_stock' if qty < reorder_level else ''
        tree.insert("", "end",
                    values=(pid, name, qty, price, supplier_name, barcode or "", reorder_level),
                    tags=(tag,))

def show_suppliers():
    for row in tree.get_children():
        tree.delete(row)
    tree["columns"] = ("ID", "Name", "Contact")
    for col in tree["columns"]:
        tree.heading(col, text=col, anchor="center")
        tree.column(col, anchor="center", width=200)
    for sid, name, contact in get_all_suppliers():
        tree.insert("", "end", values=(sid, name, contact))

def show_sales():
    for row in tree.get_children():
        tree.delete(row)
    tree["columns"] = ("Sale ID", "Product", "Quantity Sold", "Sale Date", "Total Price")
    for col in tree["columns"]:
        tree.heading(col, text=col, anchor="center")
        tree.column(col, anchor="center", width=150)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, p.name, s.quantity_sold, s.sale_date, s.total_price
        FROM sales s
        LEFT JOIN products p ON s.product_id = p.id
        ORDER BY s.sale_date DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    for sid, pname, qty, date, total in rows:
        tree.insert("", "end", values=(sid, pname, qty, date, total))

def show_reorder_alerts():
    for row in tree.get_children():
        tree.delete(row)
    tree["columns"] = ("ID", "Name", "Quantity", "Price", "Supplier", "Barcode", "Reorder Level")
    for col in tree["columns"]:
        tree.heading(col, text=col, anchor="center")
        tree.column(col, anchor="center", width=120)

    tree.tag_configure('low_stock', background="#f4848d")

    for pid, name, qty, price, supplier_id, barcode, reorder_level in get_all_products():
        if qty < reorder_level:
            supplier_name = ""
            if supplier_id:
                suppliers = get_all_suppliers()
                supplier_dict = {s[0]: s[1] for s in suppliers}
                supplier_name = supplier_dict.get(supplier_id, "")
            tree.insert("", "end",
                        values=(pid, name, qty, price, supplier_name, barcode or "", reorder_level),
                        tags=('low_stock',))


# ----------------- ANALYTICS -----------------
# ----------------- ANALYTICS -----------------
def show_analytics():
    # Clear the table_frame
    for widget in table_frame.winfo_children():
        widget.destroy()

    # Create figure
    fig, ax = plt.subplots(figsize=(7, 4))
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, SUM(s.quantity_sold) as total_qty
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.name
        ORDER BY total_qty DESC
        LIMIT 5
    """)
    rows = cursor.fetchall()
    conn.close()

    if rows:
        products = [r[0] for r in rows]
        quantities = [r[1] for r in rows]

        # Line chart
        ax.plot(products, quantities, marker='o', color="#0d1f4a", linewidth=2)

        # Labels and title
        ax.set_title("Top 5 Best-Selling Products", fontsize=14, fontweight="bold")
        ax.set_xlabel("Products", fontsize=12)
        ax.set_ylabel("Quantity Sold", fontsize=12)
        ax.grid(True, linestyle="--", alpha=0.6)

        # Straight product names (no tilt)
        ax.set_xticks(range(len(products)))
        ax.set_xticklabels(products, rotation=0, ha="center", fontsize=11)

        # Quantities above points
        for i, qty in enumerate(quantities):
            ax.text(i, qty + 0.5, str(qty), ha='center', fontsize=10, fontweight='bold')

        # ✅ Adjust spacing manually (prevents warning)
        plt.subplots_adjust(top=0.85, bottom=0.2)

    else:
        ax.text(0.5, 0.5, "No sales data available",
                ha="center", va="center", fontsize=12)
        ax.axis("off")

    # Render chart in the white dashboard area
    canvas = FigureCanvasTkAgg(fig, master=table_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)



# ----------------- FORM CREATOR -----------------
def create_form(win, fields):
    form_frame = tk.Frame(win, bg="white")
    form_frame.pack(pady=20, padx=20, fill="both", expand=True)

    entries = {}
    for i, field in enumerate(fields):
        label, ftype, default, values = field
        tk.Label(form_frame, text=label, font=("Segoe UI", 11, "bold"),
                 bg="white", anchor="w").grid(row=i, column=0, padx=10, pady=10, sticky="w")

        if ftype == "entry":
            entry = tk.Entry(form_frame, font=("Segoe UI", 11), width=28)
            if default:
                entry.insert(0, default)
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="w")
            entries[label] = entry
        elif ftype == "combo":
            combo = ttk.Combobox(form_frame, values=values, state="readonly",
                                 width=26, font=("Segoe UI", 11))
            combo.grid(row=i, column=1, padx=10, pady=10, sticky="w")
            entries[label] = combo
    return entries

# ----------------- ADD PRODUCT -----------------
def add_product_ui():
    win = tk.Toplevel(root)
    win.title("Add Product")
    win.geometry("450x420")
    win.config(bg="white")
    win.resizable(False, False)

    suppliers = get_all_suppliers()
    supplier_dict = {s[1]: s[0] for s in suppliers}

    fields = [
        ("Product Name:", "entry", "", None),
        ("Quantity:", "entry", "", None),
        ("Price:", "entry", "", None),
        ("Supplier:", "combo", "", list(supplier_dict.keys())),
        ("Barcode:", "entry", "", None),
        ("Reorder Level:", "entry", "10", None),
    ]

    entries = create_form(win, fields)

    def save():
        try:
            supplier_id = supplier_dict.get(entries["Supplier:"].get())
            reorder_val = entries["Reorder Level:"].get().strip()
            reorder_level = int(reorder_val) if reorder_val else 10

            add_product(
                entries["Product Name:"].get(),
                int(entries["Quantity:"].get()),
                float(entries["Price:"].get()),
                supplier_id=supplier_id,
                barcode=entries["Barcode:"].get() or None,
                reorder_level=reorder_level
            )
            messagebox.showinfo("Success", "✅ Product added successfully")
            win.destroy()
            show_products()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(win, text=" Save Product", command=save,
              bg="#0d1f4a", fg="white", font=("Segoe UI", 12, "bold"),
              width=18, height=1, relief="flat").pack(pady=15)

# ----------------- ADD SUPPLIER -----------------
def add_supplier_ui():
    win = tk.Toplevel(root)
    win.title("Add Supplier")
    win.geometry("400x250")
    win.config(bg="white")
    win.resizable(False, False)

    fields = [
        ("Supplier Name:", "entry", "", None),
        ("Contact:", "entry", "", None),
    ]
    entries = create_form(win, fields)

    def save():
        add_supplier(entries["Supplier Name:"].get(), entries["Contact:"].get())
        messagebox.showinfo("Success", "✅ Supplier added successfully")
        win.destroy()
        show_suppliers()

    tk.Button(win, text=" Save Supplier", command=save,
              bg="#0d1f4a", fg="white", font=("Segoe UI", 12, "bold"),
              width=18, height=1, relief="flat").pack(pady=15)

# ----------------- RECORD SALE -----------------
def record_sale_ui():
    win = tk.Toplevel(root)
    win.title("Record Sale")
    win.geometry("400x300")
    win.config(bg="white")
    win.resizable(False, False)

    fields = [
        ("Product ID:", "entry", "", None),
        ("OR Scan Barcode:", "entry", "", None),
        ("Quantity:", "entry", "", None),
    ]
    entries = create_form(win, fields)
    barcode_entry = entries["OR Scan Barcode:"]
    barcode_entry.focus()
    barcode_entry.bind("<Return>", lambda event: save())

    def save():
        try:
            product_id = entries["Product ID:"].get().strip()
            barcode = entries["OR Scan Barcode:"].get().strip()

            if barcode:
                product = get_product_by_barcode(barcode)
                if not product:
                    raise ValueError("❌ Barcode not found")
                product_id = product[0]

            if not product_id:
                raise ValueError("❌ Enter Product ID or Barcode")

            alert = record_sale(int(product_id), int(entries["Quantity:"].get()))
            messagebox.showinfo("Success", "✅ Sale recorded successfully")
            if alert:
                messagebox.showwarning("Reorder Alert", "⚠️ Stock is below reorder level!")
            win.destroy()
            show_products()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(win, text=" Save Sale", command=save,
              bg="#0d1f4a", fg="white", font=("Segoe UI", 12, "bold"),
              width=18, height=1, relief="flat").pack(pady=15)

# ----------------- RESET DATABASE -----------------
def reset_database_ui():
    confirm = messagebox.askyesno("Confirm", "This will CLEAR ALL DATA. Continue?")
    if confirm:
        reset_database()
        messagebox.showinfo("Success", "✅ All data reset")
        show_products()
        show_suppliers()

# ----------------- SIDEBAR BUTTONS -----------------
create_sidebar_button("Add Product", add_product_ui).pack(pady=6, fill="x")
create_sidebar_button("View Products", show_products).pack(pady=6, fill="x")
create_sidebar_button("Record Sale", record_sale_ui).pack(pady=6, fill="x")
create_sidebar_button("Add Supplier", add_supplier_ui).pack(pady=6, fill="x")
create_sidebar_button("View Suppliers", show_suppliers).pack(pady=6, fill="x")
create_sidebar_button("View Sales", show_sales).pack(pady=6, fill="x")
create_sidebar_button("Reorder Alerts", show_reorder_alerts).pack(pady=6, fill="x")
create_sidebar_button("Analytics", show_analytics).pack(pady=6, fill="x")  # ✅ New
create_sidebar_button("Reset Database", reset_database_ui).pack(pady=15, fill="x")
create_sidebar_button("Exit", root.quit, "red").pack(pady=15, fill="x")

root.mainloop()
