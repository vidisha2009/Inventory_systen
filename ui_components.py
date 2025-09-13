def record_sale_ui():
    sale_win = tk.Toplevel()
    sale_win.title("Record Sale")
    sale_win.geometry("300x250")

    tk.Label(sale_win, text="Enter Product ID or Scan Barcode").pack(pady=5)
    barcode_entry = tk.Entry(sale_win)
    barcode_entry.pack(pady=5)

    tk.Label(sale_win, text="Quantity Sold").pack(pady=5)
    qty_entry = tk.Entry(sale_win)
    qty_entry.pack(pady=5)

    def save_sale():
        product_id_or_code = barcode_entry.get().strip()
        quantity = int(qty_entry.get())

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()

        # 🔍 Check if input is product ID or barcode (future extension)
        cursor.execute("SELECT id, name, quantity FROM products WHERE id=?", (product_id_or_code,))
        product = cursor.fetchone()

        if product:
            product_id, name, stock = product
            if stock - quantity < 0:
                messagebox.showerror("Error", f"Not enough stock for {name}")
            else:
                cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (quantity, product_id))
                cursor.execute("INSERT INTO sales (product_id, quantity) VALUES (?, ?)", (product_id, quantity))
                conn.commit()
                messagebox.showinfo("Success", f"Sale recorded for {name}")
        else:
            messagebox.showerror("Error", "Product not found")

        conn.close()
        sale_win.destroy()

    tk.Button(sale_win, text="Save", command=save_sale).pack(pady=20)
