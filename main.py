import tkinter as tk
from tkinter import messagebox, ttk
import hashlib
from datetime import datetime, timedelta
from db import create_connection, create_tables
import tkinter.simpledialog as simpledialog

# Added imports for matplotlib
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ShopManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shop Management System - Dashboard")
        self.root.geometry("600x500")
        self.root.configure(bg="#34495e")
        
        # Center the window
        self.center_window()
        
        try:
            create_tables()
            self.conn = create_connection()
            self.current_user = "admin"  # Set a default user or None
            self.show_dashboard()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {str(e)}")
            self.root.destroy()

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    # Removed login method and login UI


    def show_dashboard(self):
        """Show main dashboard with modern UI"""
        self.clear_window()
        self.root.geometry("600x500")
        self.root.title("Shop Management System - Dashboard")
        self.root.configure(bg="#34495e")
        
        # Header frame
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Welcome message
        welcome_label = tk.Label(header_frame, text=f"Welcome, {self.current_user}!", 
                               font=("Arial", 40, "bold"), bg="#2c3e50", fg="#ecf0f1")
        welcome_label.pack(pady=15)
        
        # --- Low-stock banner ---
        cur = self.conn.cursor()
        low = cur.execute("SELECT name FROM products WHERE stock < alert_threshold").fetchall()
        if low:
            banner = "⚠️ Low stock: " + ", ".join([l[0] for l in low])
            tk.Label(header_frame, text=banner, bg="#2c3e50", fg="#e74c3c",
                     font=("Arial", 15, "bold")).pack(pady=(0, 5))
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg="#34495e")
        content_frame.pack(expand=True, fill='both', padx=50, pady=30)
        
        # Button style
        btn_style = {
            "width": 25, "height": 2,
            "font": ("Arial", 12, "bold"),
            "bg": "#3498db", "fg": "white",
            "relief": "flat", "cursor": "hand2",
            "activebackground": "#2980b9"
        }
        
        # Dashboard buttons
        buttons = [
            ("📊 Record Transaction", self.record_transaction),
            ("📦 Manage Stock", self.manage_stock),
            ("🛒 Point of Sale (POS)", self.pos_system),
            ("📈 Sales Reports", self.sales_reports),
            ("🚪 Logout", self.logout)
        ]
        
        for text, command in buttons:
            btn = tk.Button(content_frame, text=text, command=command, **btn_style)
            btn.pack(pady=10)
            
            # Add hover effect
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2980b9"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#3498db"))

    def record_transaction(self):
        """Record a new transaction"""
        self.clear_window()
        self.root.geometry("500x400")
        self.root.configure(bg="#34495e")
        self.root.title("Shop Management System - Record Transaction")
        
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Record Transaction", 
                font=("Arial", 16, "bold"), bg="#2c3e50", fg="#ecf0f1").pack(pady=15)
        
        # Content frame
        content_frame = tk.Frame(self.root, bg="#34495e")
        content_frame.pack(expand=True, fill='both', padx=40, pady=30)
        
        # Product selection
        tk.Label(content_frame, text="Select Product:", bg="#34495e", fg="#ecf0f1",
                font=("Arial", 12)).pack(anchor='w', pady=(0, 5))
        
        self.product_var = tk.StringVar()
        self.product_dropdown = ttk.Combobox(content_frame, textvariable=self.product_var,
                                           font=("Arial", 12), state="readonly")
        self.product_dropdown.pack(fill='x', pady=(0, 20))
        
        # Quantity
        tk.Label(content_frame, text="Quantity:", bg="#34495e", fg="#ecf0f1",
                font=("Arial", 12)).pack(anchor='w', pady=(0, 5))
        self.quantity_entry = tk.Entry(content_frame, font=("Arial", 12),
                                      bg="#2c3e50", fg="#ecf0f1", relief='flat',
                                      insertbackground="#ecf0f1")
        self.quantity_entry.pack(fill='x', pady=(0, 30), ipady=8)
        
        # Buttons frame
        btn_frame = tk.Frame(content_frame, bg="#34495e")
        btn_frame.pack(fill='x')
        
        record_btn = tk.Button(btn_frame, text="Record Transaction", 
                             command=self.save_transaction,
                             bg="#27ae60", fg="white", font=("Arial", 12, "bold"),
                             relief='flat', cursor="hand2", activebackground="#229954")
        record_btn.pack(side='left', padx=(0, 10), pady=10, ipadx=20, ipady=8)
        
        back_btn = tk.Button(btn_frame, text="Back to Dashboard", 
                           command=self.show_dashboard,
                           bg="#95a5a6", fg="white", font=("Arial", 12, "bold"),
                           relief='flat', cursor="hand2", activebackground="#7f8c8d")
        back_btn.pack(side='left', pady=10, ipadx=20, ipady=8)
        
        # Bind Enter key
        self.root.bind('<Return>', lambda event: self.save_transaction())
        
        self.load_products()
        self.quantity_entry.focus()

    def load_products(self):
        """Load products into dropdown"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name FROM products ORDER BY name")
            products = cursor.fetchall()
            
            self.products_dict = {}
            product_names = []
            
            for prod_id, prod_name in products:
                self.products_dict[prod_name] = prod_id
                product_names.append(prod_name)
            
            self.product_dropdown['values'] = product_names
            if product_names:
                self.product_dropdown.set(product_names[0])
            else:
                self.product_dropdown.set("")
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load products: {str(e)}")

    def save_transaction(self):
        """Save transaction to database"""
        product_name = self.product_var.get()
        quantity_str = self.quantity_entry.get().strip()
        
        if not product_name:
            messagebox.showerror("Error", "Please select a product")
            return
        
        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive quantity")
            return
        
        try:
            product_id = self.products_dict.get(product_name)
            cursor = self.conn.cursor()
            cursor.execute("SELECT price, stock FROM products WHERE id=?", (product_id,))
            row = cursor.fetchone()
            
            if not row:
                messagebox.showerror("Error", "Selected product not found")
                return
            
            price, stock = row
            
            if quantity > stock:
                messagebox.showerror("Error", f"Insufficient stock. Available: {stock}")
                return
            
            total_price = price * quantity
            transaction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Insert transaction
            cursor.execute("""
                INSERT INTO transactions (product_id, quantity, total_price, transaction_date)
                VALUES (?, ?, ?, ?)
            """, (product_id, quantity, total_price, transaction_date))
            
            # Update stock
            new_stock = stock - quantity
            cursor.execute("UPDATE products SET stock=? WHERE id=?", (new_stock, product_id))
            
            self.conn.commit()
            messagebox.showinfo("Success", f"Transaction recorded successfully!\nTotal: ${total_price:.2f}")
            self.show_dashboard()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save transaction: {str(e)}")

    def manage_stock(self):
        """Stock management interface"""
        self.clear_window()
        self.root.geometry("800x600")
        self.root.title("Shop Management System - Stock Management")
        self.root.configure(bg="#34495e")
        
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Stock Management", 
                font=("Arial", 20, "bold"), bg="#2c3e50", fg="#ecf0f1").pack(pady=15)
        
        # Content frame
        content_frame = tk.Frame(self.root, bg="#34495e")
        content_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Stock table with scrollbar
        list_frame = tk.Frame(content_frame, bg="#34495e")
        list_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        columns = ("Name", "Stock", "Price", "Cost Price", "Alert Threshold")
        self.stock_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.stock_tree.heading(col, text=col)
            self.stock_tree.column(col, anchor="center")
        self.stock_tree.pack(side='left', fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.stock_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.stock_tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        btn_frame = tk.Frame(content_frame, bg="#34495e")
        btn_frame.pack(fill='x')
        
        btn_style = {
            "font": ("Arial", 15, "bold"),
            "relief": "flat", "cursor": "hand2",
            "fg": "white", "activebackground": "#2980b9"
        }
        
        add_btn = tk.Button(btn_frame, text="Add New Product", 
                          command=self.add_product_ui,
                          bg="#27ae60", **btn_style)
        add_btn.pack(side='left', padx=(0, 10), pady=5, ipadx=15, ipady=8)
        
        update_btn = tk.Button(btn_frame, text="Update Selected Product", 
                             command=self.update_product_stock_ui,
                             bg="#f39c12", **btn_style)
        update_btn.pack(side='left', padx=(0, 10), pady=5, ipadx=15, ipady=8)
        
        refresh_btn = tk.Button(btn_frame, text="Refresh Stock", 
                            command=self.load_stock,
                            bg="#2980b9", fg="white", font=("Arial", 15, "bold"),
                            relief="flat", cursor="hand2")
        refresh_btn.pack(side='left', padx=(0, 10), pady=5, ipadx=15, ipady=8)
        
        back_btn = tk.Button(btn_frame, text="Back to Dashboard", 
                           command=self.show_dashboard,
                           bg="#95a5a6", **btn_style)
        back_btn.pack(side='right', pady=5, ipadx=15, ipady=8)
        
        self.load_stock()

    def load_stock(self):
        """Load stock information"""
        try:
            # Check if stock_tree widget exists and is visible before updating
            if not hasattr(self, 'stock_tree') or not self.stock_tree.winfo_exists():
                return
            
            for row in self.stock_tree.get_children():
                self.stock_tree.delete(row)
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name, stock, alert_threshold, price, cost_price FROM products ORDER BY name")
            products = cursor.fetchall()
            
            total_stock_value = 0.0
            low_stock_alerts = []
            for prod_id, name, stock, alert_threshold, price, cost_price in products:
                self.stock_tree.insert("", "end", values=(name, stock, f"${price:.2f}", f"${cost_price:.2f}", alert_threshold))
                total_stock_value += stock * cost_price
                if stock < alert_threshold:
                    low_stock_alerts.append(name)
            
            # Display total stock value
            if hasattr(self, 'total_value_label') and self.total_value_label.winfo_exists():
                self.total_value_label.config(text=f"Total Stock Value: ${total_stock_value:.2f}")
                self.total_value_label.update_idletasks()
                self.total_value_label.update()
            else:
                self.total_value_label = tk.Label(self.root, text=f"Total Stock Value: ${total_stock_value:.2f}",
                                         font=("Arial", 16, "bold"), bg="#34495e", fg="#ecf0f1")
                self.total_value_label.pack(pady=(0, 10))
            
            if low_stock_alerts:
                alert_msg = "Low stock alert for:\n" + "\n".join(low_stock_alerts)
                messagebox.showwarning("Stock Alert", alert_msg)
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load stock: {str(e)}")

    def add_product_ui(self):
        """Add new product – keeps kimi.py styling, clearer buttons"""
        self.create_product_popup("Add New Product", self.add_product)

    def update_product_stock_ui(self):
        """Update product – keeps kimi.py styling, clearer buttons"""
        selected = self.stock_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a product to update")
            return
        item_id = selected[0]
        prod_name = self.stock_tree.item(item_id, 'values')[0]
        cur = self.conn.cursor()
        cur.execute("SELECT name, price, description, stock, alert_threshold, cost_price FROM products WHERE name=?", (prod_name,))
        prod = cur.fetchone()
        if not prod:
            messagebox.showerror("Error", "Product not found")
            return
        self.create_product_popup("Update Product", lambda: self.update_product_details(prod_name), prod)

    def create_product_popup(self, title, save_command, product_data=None):
        """Re-usable popup styled exactly like kimi.py"""
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("400x850")
        popup.configure(bg="#34495e")
        popup.transient(self.root)
        popup.deiconify()
        popup.wait_visibility()
        popup.grab_set()

        # Center
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - 200
        y = (popup.winfo_screenheight() // 2) - 250
        popup.geometry(f"+{x}+{y}")

        content = tk.Frame(popup, bg="#34495e")
        content.pack(fill="both", expand=True, padx=30, pady=30)

        tk.Label(content, text=title, font=("Arial", 16, "bold"),
                 bg="#34495e", fg="#ecf0f1").pack(pady=(0, 20))

        fields = [("Product Name:", "name"),
                  ("Price:", "price"),
                  ("Cost Price:", "cost_price"),
                  ("Description:", "description"),
                  ("Current Stock Quantity:", "current_stock"),
                  ("Add Quantity:", "add_stock"),
                  ("Alert Threshold:", "alert")]

        self.popup_entries = {}
        for label, key in fields:
            tk.Label(content, text=label, bg="#34495e", fg="#ecf0f1",
                     font=("Arial", 12)).pack(anchor="w", pady=(10, 5))
            if key == "current_stock":
                # Show current stock as label (read-only)
                self.current_stock_label = tk.Label(content, text="", font=("Arial", 12), bg="#2c3e50", fg="#ecf0f1")
                self.current_stock_label.pack(fill="x", ipady=8)
            else:
                ent = tk.Entry(content, font=("Arial", 12), bg="#2c3e50",
                               fg="#ecf0f1", relief="flat", insertbackground="#ecf0f1")
                ent.pack(fill="x", ipady=8)
                self.popup_entries[key] = ent

        # Pre-fill if updating
        if product_data:
            self.popup_entries["name"].insert(0, product_data[0])
            self.popup_entries["price"].insert(0, str(product_data[1]))
            self.popup_entries["cost_price"].insert(0, str(product_data[5]))
            self.popup_entries["description"].insert(0, product_data[2] or "")
            self.current_stock_label.config(text=str(product_data[3]))
            self.popup_entries["add_stock"].insert(0, "0")
            self.popup_entries["alert"].insert(0, str(product_data[4]))
        else:
            self.popup_entries["alert"].insert(0, "5")

        btn_frame = tk.Frame(content, bg="#34495e")
        btn_frame.pack(fill="x", pady=(20, 0))
        save_btn = tk.Button(btn_frame, text="Save", command=lambda: self.save_product(save_command, popup),
                  bg="#27ae60", fg="white", font=("Arial", 12, "bold"),
                  relief="flat", cursor="hand2")
        save_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=20, ipady=8)
        cancel_btn = tk.Button(btn_frame, text="Cancel", command=popup.destroy,
                  bg="#e74c3c", fg="white", font=("Arial", 12, "bold"),
                  relief="flat", cursor="hand2")
        cancel_btn.pack(side=tk.LEFT, ipadx=20, ipady=8)

        self.popup_entries["name"].focus()

    def save_product(self, save_command, popup):
        """Called by both Add & Update – runs the passed save_command"""
        save_command()
        popup.destroy()
        self.load_stock()

    def add_product(self):
        """Add new product to database"""
        try:
            name = self.popup_entries["name"].get().strip()
            price_str = self.popup_entries["price"].get().strip()
            cost_price_str = self.popup_entries["cost_price"].get().strip()
            description = self.popup_entries["description"].get().strip()
            add_stock_str = self.popup_entries["add_stock"].get().strip()
            alert_str = self.popup_entries["alert"].get().strip()
            
            if not name or not price_str or not add_stock_str or not cost_price_str:
                messagebox.showerror("Error", "Please fill in all required fields")
                return
            
            price = float(price_str)
            cost_price = float(cost_price_str)
            stock = int(add_stock_str)
            alert_threshold = int(alert_str) if alert_str else 5
            
            if price < 0 or cost_price < 0 or stock < 0 or alert_threshold < 0:
                messagebox.showerror("Error", "Values cannot be negative")
                return
            
            cursor = self.conn.cursor()
            # Check if product with same name exists
            cursor.execute("SELECT COUNT(*) FROM products WHERE name=?", (name,))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", f"Product '{name}' already exists.")
                return
            
            cursor.execute("""
                INSERT INTO products (name, price, cost_price, description, stock, alert_threshold) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, price, cost_price, description, stock, alert_threshold))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Product added successfully!")
            self.load_stock()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add product: {str(e)}")

    def update_product_details(self, old_product_name):
        """Update product details"""
        try:
            name = self.popup_entries["name"].get().strip()
            price_str = self.popup_entries["price"].get().strip()
            cost_price_str = self.popup_entries["cost_price"].get().strip()
            description = self.popup_entries["description"].get().strip()
            add_stock_str = self.popup_entries["add_stock"].get().strip()
            alert_str = self.popup_entries["alert"].get().strip()
            
            if not name or not price_str or not add_stock_str or not cost_price_str:
                messagebox.showerror("Error", "Please fill in all required fields")
                return
            
            price = float(price_str)
            cost_price = float(cost_price_str)
            add_stock = int(add_stock_str)
            alert_threshold = int(alert_str) if alert_str else 5
            
            if price < 0 or cost_price < 0 or add_stock < 0 or alert_threshold < 0:
                messagebox.showerror("Error", "Values cannot be negative")
                return
            
            cursor = self.conn.cursor()
            # Get old cost price and current stock
            cursor.execute("SELECT cost_price, stock FROM products WHERE name=?", (old_product_name,))
            old_row = cursor.fetchone()
            old_cost_price = old_row[0] if old_row else 0.0
            current_stock = old_row[1] if old_row else 0
            
            new_stock = current_stock + add_stock
            
            cursor.execute("""
                UPDATE products 
                SET name=?, price=?, cost_price=?, description=?, stock=?, alert_threshold=?
                WHERE name=?
            """, (name, price, cost_price, description, new_stock, alert_threshold, old_product_name))
            
            # Insert cost price change if changed
            if cost_price != old_cost_price:
                change_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""
                    INSERT INTO cost_price_history (product_id, old_cost_price, new_cost_price, change_date)
                    SELECT id, ?, ?, ? FROM products WHERE name=?
                """, (old_cost_price, cost_price, change_date, name))
            
            self.conn.commit()
            self.load_stock()
            messagebox.showinfo("Success", "Product updated successfully!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update product: {str(e)}")

    def pos_system(self):
        """Point of Sale system"""
        self.clear_window()
        self.root.geometry("800x700")
        self.root.title("Shop Management System - Point of Sale")
        self.root.configure(bg="#34495e")
        
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Point of Sale (POS)", 
                font=("Arial", 25, "bold"), bg="#2c3e50", fg="#ecf0f1").pack(pady=15)
        
        # Main content
        main_frame = tk.Frame(self.root, bg="#34495e")
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Left side - Product selection
        left_frame = tk.Frame(main_frame, bg="#34495e")
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(left_frame, text="Product Selection", font=("Arial", 20, "bold"),
                bg="#34495e", fg="#ecf0f1").pack(pady=(0, 10))
        
        tk.Label(left_frame, text="Select Product:", bg="#34495e", fg="#ecf0f1",
                font=("Arial", 20)).pack(anchor='w', pady=(0, 5))
        
        # Search entry for filtering products
        self.pos_search_var = tk.StringVar()
        self.pos_search_entry = tk.Entry(left_frame, textvariable=self.pos_search_var,
                                         font=("Arial", 20
                                         ), bg="#2c3e50", fg="#ecf0f1",
                                         relief='flat', insertbackground="#ecf0f1")
        self.pos_search_entry.pack(fill='x', pady=(0, 10))
        self.pos_search_entry.bind('<KeyRelease>', self.pos_filter_products)
        
        self.pos_product_var = tk.StringVar()
        self.pos_product_dropdown = ttk.Combobox(left_frame, textvariable=self.pos_product_var,
                                               font=("Arial", 20), state="readonly")
        self.pos_product_dropdown.pack(fill='x', pady=(0, 15))
        
        tk.Label(left_frame, text="Quantity:", bg="#34495e", fg="#eef1ec",
                font=("Arial", 12)).pack(anchor='w', pady=(0, 5))
        
        self.pos_quantity_entry = tk.Entry(left_frame, font=("Arial", 12),
                                         bg="#2c3e50", fg="#ecf0f1", relief='flat',
                                         insertbackground="#ecf0f1")
        self.pos_quantity_entry.pack(fill='x', pady=(0, 15), ipady=8)
        
        add_btn = tk.Button(left_frame, text="Add to Cart", command=self.pos_add_to_cart,
                          bg="#27ae60", fg="white", font=("Arial", 15, "bold"),
                          relief='flat', cursor="hand2")
        add_btn.pack(fill='x', pady=(0, 20), ipady=10)
        
        # Right side - Cart
        right_frame = tk.Frame(main_frame, bg="#34495e")
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        tk.Label(right_frame, text="Shopping Cart", font=("Arial", 14, "bold"),
                bg="#34495e", fg="#ecf0f1").pack(pady=(0, 10))
        
        # Cart listbox with scrollbar
        cart_frame = tk.Frame(right_frame, bg="#34495e")
        cart_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        cart_scrollbar = tk.Scrollbar(cart_frame)
        cart_scrollbar.pack(side='right', fill='y')
        
        self.cart_listbox = tk.Listbox(cart_frame, yscrollcommand=cart_scrollbar.set,
                                      font=("Arial", 11), bg="#2c3e50", fg="#ecf0f1",
                                      selectbackground="#3498db", relief='flat')
        self.cart_listbox.pack(side='left', fill='both', expand=True)
        cart_scrollbar.config(command=self.cart_listbox.yview)
        
        # Total label
        self.total_label = tk.Label(right_frame, text="Total: $0.00", 
                                   font=("Arial", 14, "bold"), bg="#34495e", fg="#ecf0f1")
        self.total_label.pack(pady=(0, 15))
        
        # Action buttons
        btn_frame = tk.Frame(right_frame, bg="#34495e")
        btn_frame.pack(fill='x')
        
        complete_btn = tk.Button(btn_frame, text="Complete Sale", 
                               command=self.pos_complete_sale,
                               bg="#3498db", fg="white", font=("Arial", 12, "bold"),
                               relief='flat', cursor="hand2")
        complete_btn.pack(fill='x', pady=(0, 10), ipady=10)
        
        clear_btn = tk.Button(btn_frame, text="Clear Cart", 
                            command=self.pos_clear_cart,
                            bg="#e74c3c", fg="white", font=("Arial", 12, "bold"),
                            relief='flat', cursor="hand2")
        clear_btn.pack(fill='x', pady=(0, 10), ipady=10)
        
        # Bottom navigation
        nav_frame = tk.Frame(self.root, bg="#34495e")
        nav_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        back_btn = tk.Button(nav_frame, text="Back to Dashboard", 
                           command=self.show_dashboard,
                           bg="#95a5a6", fg="white", font=("Arial", 12, "bold"),
                           relief='flat', cursor="hand2")
        back_btn.pack(side='right', ipadx=20, ipady=8)
        
        self.pos_cart = []
        self.pos_total = 0.0
        self.load_pos_products()
        self.pos_quantity_entry.focus()

    def load_pos_products(self):
        """Load products for POS system"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name, stock, cost_price FROM products WHERE stock > 0 ORDER BY name")
            products = cursor.fetchall()
            
            self.pos_products_dict = {}
            self.pos_all_product_names = []
            
            for prod_id, prod_name, stock, cost_price in products:
                self.pos_products_dict[prod_name] = (prod_id, stock, cost_price)
                self.pos_all_product_names.append(prod_name)
            
            self.pos_product_dropdown['values'] = self.pos_all_product_names
            if self.pos_all_product_names:
                self.pos_product_dropdown.set(self.pos_all_product_names[0])
            else:
                self.pos_product_dropdown.set("")
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load products: {str(e)}")

    def pos_add_to_cart(self):
        """Add item to cart"""
        product_name = self.pos_product_var.get()
        quantity_str = self.pos_quantity_entry.get().strip()
        
        if not product_name:
            messagebox.showerror("Error", "Please select a product")
            return
        
        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive quantity")
            return
        
        try:
            product_id, available_stock, _ = self.pos_products_dict.get(product_name)
            cursor = self.conn.cursor()
            cursor.execute("SELECT price FROM products WHERE id=?", (product_id,))
            price = cursor.fetchone()[0]
            
            # Check if already in cart
            cart_quantity = sum(item[2] for item in self.pos_cart if item[0] == product_id)
            total_quantity = cart_quantity + quantity
            
            if total_quantity > available_stock:
                messagebox.showerror("Error", f"Insufficient stock. Available: {available_stock}, In cart: {cart_quantity}")
                return
            
            # If product already in cart, update quantity instead of adding duplicate
            for i, item in enumerate(self.pos_cart):
                if item[0] == product_id:
                    new_quantity = item[2] + quantity
                    self.pos_cart[i] = (product_id, product_name, new_quantity, price)
                    self.update_cart_display()
                    self.pos_quantity_entry.delete(0, tk.END)
                    self.pos_quantity_entry.focus()
                    return
            self.pos_cart.append((product_id, product_name, quantity, price))
            
            self.update_cart_display()
            self.pos_quantity_entry.delete(0, tk.END)
            self.pos_quantity_entry.focus()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add to cart: {str(e)}")

    def update_cart_display(self):
        """Update cart display"""
        self.cart_listbox.delete(0, tk.END)
        self.pos_total = 0.0
        self.pos_profit_total = 0.0
        
        for item in self.pos_cart:
            product_id, product_name, quantity, price = item
            _, _, cost_price = self.pos_products_dict.get(product_name, (None, None, 0.0))
            item_total = quantity * price
            profit = (price - cost_price) * quantity
            self.pos_total += item_total
            self.pos_profit_total += profit
            
            display_text = f"{product_name} x {quantity} @ ${price:.2f} = ${item_total:.2f} | Profit: ${profit:.2f}"
            self.cart_listbox.insert(tk.END, display_text)
        
        self.total_label.config(text=f"Total: ${self.pos_total:.2f} | Total Profit: ${self.pos_profit_total:.2f}")

    def pos_clear_cart(self):
        """Clear the cart"""
        if self.pos_cart:
            if messagebox.askyesno("Confirm", "Are you sure you want to clear the cart?"):
                self.pos_cart.clear()
                self.update_cart_display()

    def pos_complete_sale(self):
        """Complete the sale"""
        if not self.pos_cart:
            messagebox.showerror("Error", "Cart is empty")
            return
        
        if not messagebox.askyesno("Confirm Sale", f"Complete sale for ${self.pos_total:.2f}?"):
            return
        
        try:
            cursor = self.conn.cursor()
            transaction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for item in self.pos_cart:
                product_id, product_name, quantity, price = item
                total_price = price * quantity
                
                # Insert transaction
                cursor.execute("""
                    INSERT INTO transactions (product_id, quantity, total_price, transaction_date)
                    VALUES (?, ?, ?, ?)
                """, (product_id, quantity, total_price, transaction_date))
                
                # Update stock
                cursor.execute("SELECT stock FROM products WHERE id=?", (product_id,))
                current_stock = cursor.fetchone()[0]
                new_stock = current_stock - quantity
                cursor.execute("UPDATE products SET stock=? WHERE id=?", (new_stock, product_id))
            
            self.conn.commit()
            messagebox.showinfo("Sale Complete", f"Sale completed successfully!\nTotal: ${self.pos_total:.2f}")
            
            self.pos_cart.clear()
            self.update_cart_display()
            self.load_pos_products()
            self.load_stock()  # Refresh stock display after sale
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to complete sale: {str(e)}")

    def sales_reports(self):
        """Sales reports with improved UI"""
        self.clear_window()
        self.root.geometry("900x700")
        self.root.title("Shop Management System - Sales Reports")
        self.root.configure(bg="#34495e")
        
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Sales Reports", 
                font=("Arial", 20, "bold"), bg="#2c3e50", fg="#ecf0f1").pack(pady=15)
        
        # Main content
        main_frame = tk.Frame(self.root, bg="#34495e")
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Summary frame
        summary_frame = tk.Frame(main_frame, bg="#2c3e50", relief='flat', bd=2)
        summary_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(summary_frame, text="Sales Summary", font=("Arial", 14, "bold"),
                bg="#2c3e50", fg="#ecf0f1").pack(pady=10)
        
        try:
            cursor = self.conn.cursor()
            today = datetime.now().date()
            
            # Today's sales
            cursor.execute("""
                SELECT SUM(total_price) FROM transactions
                WHERE DATE(transaction_date) = ?
            """, (today.strftime("%Y-%m-%d"),))
            today_sales = cursor.fetchone()[0] or 0.0
            
            # This month's sales
            first_day_month = today.replace(day=1)
            cursor.execute("""
                SELECT SUM(total_price) FROM transactions
                WHERE DATE(transaction_date) >= ?
            """, (first_day_month.strftime("%Y-%m-%d"),))
            month_sales = cursor.fetchone()[0] or 0.0
            
            # This year's sales
            first_day_year = today.replace(month=1, day=1)
            cursor.execute("""
                SELECT SUM(total_price) FROM transactions
                WHERE DATE(transaction_date) >= ?
            """, (first_day_year.strftime("%Y-%m-%d"),))
            year_sales = cursor.fetchone()[0] or 0.0
            
            summary_text = f"Today: ${today_sales:.2f}  |  This Month: ${month_sales:.2f}  |  This Year: ${year_sales:.2f}"
            tk.Label(summary_frame, text=summary_text, font=("Arial", 12),
                    bg="#2c3e50", fg="#ecf0f1").pack(pady=(0, 10))
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load sales summary: {str(e)}")
        
        # Date selection frame
        date_frame = tk.Frame(main_frame, bg="#34495e")
        date_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(date_frame, text="Select Date (YYYY-MM-DD):", bg="#34495e", fg="#ecf0f1",
                font=("Arial", 15)).pack(side='left', padx=(0, 10))
        
        self.date_entry = tk.Entry(date_frame, font=("Arial", 12), bg="#2c3e50", 
                                  fg="#ecf0f1", relief='flat', insertbackground="#ecf0f1")
        self.date_entry.pack(side='left', padx=(0, 10), ipady=5)
        self.date_entry.insert(0, today.strftime("%Y-%m-%d"))
        
        load_btn = tk.Button(date_frame, text="Load Sales", 
                           command=self.load_sales_for_date,
                           bg="#3498db", fg="white", font=("Arial", 12, "bold"),
                           relief='flat', cursor="hand2")
        load_btn.pack(side='left', ipadx=15, ipady=5)

        save_csv_btn = tk.Button(date_frame, text="Save to CSV",
                                 command=self.save_sales_to_csv,
                                 bg="#27ae60", fg="white", font=("Arial", 12, "bold"),
                                 relief='flat', cursor="hand2")
        save_csv_btn.pack(side='left', padx=(10, 0), ipadx=15, ipady=5)
        
        # Sales details frame
        details_frame = tk.Frame(main_frame, bg="#34495e")
        details_frame.pack(fill='both', expand=True)
        
        tk.Label(details_frame, text="Sales Details", font=("Arial", 20, "bold"),
                bg="#34495e", fg="#ecf0f1").pack(pady=(0, 10))
        
        # Sales listbox with scrollbar
        sales_list_frame = tk.Frame(details_frame, bg="#34495e")
        sales_list_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        columns = ("Time", "Product Name", "Quantity", "Total Price", "Profit")
        self.sales_tree = ttk.Treeview(sales_list_frame, columns=columns, show="headings")
        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, anchor="center")
        self.sales_tree.pack(side='left', fill='both', expand=True)
        
        sales_scrollbar = tk.Scrollbar(sales_list_frame, orient="vertical", command=self.sales_tree.yview)
        sales_scrollbar.pack(side='right', fill='y')
        self.sales_tree.configure(yscrollcommand=sales_scrollbar.set)
        
        # Navigation
        nav_frame = tk.Frame(main_frame, bg="#34495e")
        nav_frame.pack(fill='x')
        
        back_btn = tk.Button(nav_frame, text="Back to Dashboard", 
                           command=self.show_dashboard,
                           bg="#95a5a6", fg="white", font=("Arial", 15, "bold"),
                           relief='flat', cursor="hand2")
        back_btn.pack(side='right', ipadx=20, ipady=8)
        
        # Load today's sales by default
        self.load_sales_for_date()

        # Bind Ctrl+Shift+S to save sales to CSV
        self.root.bind('<Control-Shift-s>', lambda event: self.save_sales_to_csv())

        # Best/Worst Selling Products Reports Section
        reports_frame = tk.Frame(main_frame, bg="#2c3e50", relief='flat', bd=2)
        reports_frame.pack(fill='both', expand=True)
        
        tk.Label(reports_frame, text="Best/Worst Selling Products Reports", font=("Arial", 20, "bold"),
                bg="#2c3e50", fg="#ecf0f1").pack(pady=(10, 10))
        
        # Listbox with scrollbar for reports
        reports_list_frame = tk.Frame(reports_frame, bg="#2c3e50")
        reports_list_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        reports_scrollbar = tk.Scrollbar(reports_list_frame)
        reports_scrollbar.pack(side='right', fill='y')
        
        self.reports_listbox = tk.Listbox(reports_list_frame, yscrollcommand=reports_scrollbar.set,
                                         font=("Arial", 11), bg="#2c3e50", fg="#ecf0f1",
                                         selectbackground="#3498db", relief='flat')
        self.reports_listbox.pack(side='left', fill='both', expand=True)
        reports_scrollbar.config(command=self.reports_listbox.yview)
        
    def load_sales_for_date(self):
        """Load sales for specific date"""
        date_str = self.date_entry.get().strip()
        
        try:
            # Validate date format
            datetime.strptime(date_str, "%Y-%m-%d")
            
            for row in self.sales_tree.get_children():
                self.sales_tree.delete(row)
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT p.name, t.quantity, t.total_price, t.transaction_date, p.cost_price
                FROM transactions t
                JOIN products p ON t.product_id = p.id
                WHERE DATE(t.transaction_date) = ?
                ORDER BY t.transaction_date DESC
            """, (date_str,))
            
            sales = cursor.fetchall()
            
            if not sales:
                self.sales_tree.insert("", "end", values=(f"No sales recorded on {date_str}", "", "", "", ""))
                return
            
            total_day_sales = 0.0
            total_day_profit = 0.0
            for name, quantity, total_price, transaction_date, cost_price in sales:
                total_day_sales += total_price
                profit = total_price - (cost_price * quantity)
                total_day_profit += profit
                time_str = transaction_date.split()[1][:5]  # Extract time HH:MM
                self.sales_tree.insert("", "end", values=(time_str, name, quantity, f"${total_price:.2f}", f"${profit:.2f}"))
            
            self.sales_tree.insert("", "end", values=("", "", "", "", ""))
            self.sales_tree.insert("", "end", values=("Total", "", "", f"${total_day_sales:.2f}", f"${total_day_profit:.2f}"))
            
        except ValueError:
            messagebox.showerror("Error", "Please enter date in YYYY-MM-DD format")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load sales: {str(e)}")

        # Removed call to load_best_worst_reports to avoid AttributeError as method is missing
        # self.load_best_worst_reports()

    def logout(self):
        """Logout and return to login screen"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.current_user = None
            self.root.geometry("400x300")
            self.create_login_ui()

    def save_sales_to_csv(self):
        """Save sales data for selected date to CSV file"""
        import csv
        date_str = self.date_entry.get().strip()
        try:
            # Validate date format
            datetime.strptime(date_str, "%Y-%m-%d")
            
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT p.name, t.quantity, t.total_price, t.transaction_date
                FROM transactions t
                JOIN products p ON t.product_id = p.id
                WHERE DATE(t.transaction_date) = ?
                ORDER BY t.transaction_date DESC
            """, (date_str,))
            
            sales = cursor.fetchall()
            if not sales:
                messagebox.showinfo("No Data", f"No sales recorded on {date_str}")
                return
            
            filename = f"sales_{date_str}.csv"
            with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Time", "Product Name", "Quantity", "Total Price"])
                for name, quantity, total_price, transaction_date in sales:
                    time_str = transaction_date.split()[1][:5]  # Extract time HH:MM
                    writer.writerow([time_str, name, quantity, f"{total_price:.2f}"])
            
            messagebox.showinfo("Success", f"Sales data saved to {filename}")
        except ValueError:
            messagebox.showerror("Error", "Please enter date in YYYY-MM-DD format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save sales data: {str(e)}")

    def pos_filter_products(self, event=None):
        """Filter products in POS dropdown based on search entry"""
        search_text = self.pos_search_var.get().strip().lower()
        if not search_text:
            filtered = self.pos_all_product_names
        else:
            filtered = [name for name in self.pos_all_product_names if search_text in name.lower()]
        
        self.pos_product_dropdown['values'] = filtered
        if filtered:
            self.pos_product_dropdown.set(filtered[0])
        else:
            self.pos_product_dropdown.set("")

    def __del__(self):
        """Close database connection on app exit"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()


def main():
    """Main function to run the application"""
    try:
        root = tk.Tk()
        app = ShopManagementApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Application Error", f"Failed to start application: {str(e)}")


if __name__ == "__main__":
    main()