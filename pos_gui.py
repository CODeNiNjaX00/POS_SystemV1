import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import time
import os
import subprocess
from login_panel import start_login
from revenue_management_ui import ModernRevenueManagementUI
import random  # Add this import at the top of the file
import json

# Add this constant for the font
GLOBAL_FONT = ("Tajawal", 12)

def save_current_orders(orders):
    with open('current_orders.json', 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=4)
    print("Current orders saved successfully.")  # Debug print

def load_current_orders():
    if not os.path.exists('current_orders.json'):
        print("current_orders.json does not exist. Creating an empty file.")  # Debug print
        save_current_orders([])  # Create an empty file if it doesn't exist
        return []
    
    try:
        with open('current_orders.json', 'r', encoding='utf-8') as f:
            orders = json.load(f)
        print(f"Loaded {len(orders)} current orders.")  # Debug print
        return orders
    except json.JSONDecodeError:
        print("Error decoding JSON. Returning an empty list.")  # Debug print
        return []

def load_menu():
    if not os.path.exists('menu.json'):
        # Create a default menu if the file doesn't exist
        default_menu = {
            "Main Dishes": {"Burger": 50.0, "Pizza": 60.0},
            "Sides": {"Fries": 20.0, "Salad": 15.0},
            "Drinks": {"Cola": 10.0, "Water": 5.0}
        }
        save_menu(default_menu)
        return default_menu
    
    with open('menu.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_menu(menu):
    with open('menu.json', 'w', encoding='utf-8') as f:
        json.dump(menu, f, ensure_ascii=False, indent=4)

def load_orders():
    try:
        with open('orders.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("orders.json not found. Returning an empty list.")
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON in orders.json. Returning an empty list.")
        return []

def save_order(items, total, delivery_location, order_number, phone_number, delivery_fee, status='قيد التنفيذ'):
    orders = load_orders()
    new_order = {
        'order_number': order_number,
        'items': items,
        'total': total,
        'delivery_location': delivery_location,
        'phone_number': phone_number,
        'delivery_fee': delivery_fee,
        'datetime': time.strftime('%Y-%m-%d %H:%M:%S'),
        'status': status
    }
    orders.append(new_order)
    with open('orders.json', 'w', encoding='utf-8') as f:
        json.dump(orders, f, ensure_ascii=False, indent=4)

class ModernFoodOrderGUI:
    def __init__(self, master, username, role):
        self.master = master
        self.username = username
        self.role = role
        self.master.title(f"نظام طلب الطعام الحديث - مسجل دخول كـ {username} ({role})")
        
        # Set the window to full screen
        self.master.attributes('-fullscreen', True)
        
        # Set the window size to 1366x768
        self.master.geometry("1366x768")
        
        # Add a key binding to exit full screen mode
        self.master.bind('<Escape>', self.exit_fullscreen)
        
        self.master.configure(bg="#f0f0f1")

        # Set the global font
        self.master.option_add("*Font", GLOBAL_FONT)

        self.order = {}
        self.selected_category = None
        self.menu_label = None  # Initialize menu_label
        self.current_orders = load_current_orders()  # Load current orders from file

        self.menu = load_menu()
        self.create_widgets()
        self.update_datetime()
        
        self.current_orders_window = None
        self.current_orders_tree = None

    def exit_fullscreen(self, event=None):
        self.master.attributes('-fullscreen', False)
        self.master.geometry("1366x768")

    def create_widgets(self):
        # Main layout
        self.sidebar = tk.Frame(self.master, bg="#2c3e50", width=250)  # Increased width
        self.sidebar.pack(side="left", fill="y")

        self.content = tk.Frame(self.master, bg="#ecf0f1")
        self.content.pack(side="left", fill="both", expand=True)

        self.order_frame = tk.Frame(self.master, bg="#bdc3c7", width=350)  # Increased width
        self.order_frame.pack(side="right", fill="y")

        # Sidebar (Categories)
        self.create_sidebar()

        # Content (Menu items)
        self.create_content()

        # Order frame
        self.create_order_frame()

    def create_sidebar(self):
        tk.Label(self.sidebar, text="الفئات", font=(GLOBAL_FONT[0], 18, "bold"), bg="#2c3e50", fg="white").pack(pady=20)
        for category in self.menu.keys():
            btn = tk.Button(self.sidebar, text=category, command=lambda c=category: self.select_category(c),
                            bg="#34495e", fg="white", font=GLOBAL_FONT, bd=0, padx=10, pady=5, justify="right")
            btn.pack(fill="x", padx=10, pady=5)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#3498db"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#34495e"))

        if self.role == "admin":
            add_category_btn = tk.Button(self.sidebar, text="إضافة فئة", command=self.add_category,
                                         bg="#27ae60", fg="white", font=GLOBAL_FONT, bd=0, padx=10, pady=5)
            add_category_btn.pack(fill="x", padx=10, pady=5)
            add_category_btn.bind("<Enter>", lambda e, b=add_category_btn: b.config(bg="#2ecc71"))
            add_category_btn.bind("<Leave>", lambda e, b=add_category_btn: b.config(bg="#27ae60"))

            edit_category_btn = tk.Button(self.sidebar, text="تعديل فئة", command=self.edit_category,
                                         bg="#f39c12", fg="white", font=GLOBAL_FONT, bd=0, padx=10, pady=5)
            edit_category_btn.pack(fill="x", padx=10, pady=5)
            edit_category_btn.bind("<Enter>", lambda e, b=edit_category_btn: b.config(bg="#d35400"))
            edit_category_btn.bind("<Leave>", lambda e, b=edit_category_btn: b.config(bg="#f39c12"))

            view_reports_btn = tk.Button(self.sidebar, text="عرض التقارير", command=self.view_reports,
                                         bg="#9b59b6", fg="white", font=GLOBAL_FONT, bd=0, padx=10, pady=5)
            view_reports_btn.pack(fill="x", padx=10, pady=5)
            view_reports_btn.bind("<Enter>", lambda e, b=view_reports_btn: b.config(bg="#8e44ad"))
            view_reports_btn.bind("<Leave>", lambda e, b=view_reports_btn: b.config(bg="#9b59b6"))

            # Add Developer Info button (only for admin)
            developer_btn = tk.Button(self.sidebar, text="مطور التطبيق", command=self.show_developer_info,
                                      bg="#3498db", fg="white", font=GLOBAL_FONT, bd=0, padx=10, pady=5)
            developer_btn.pack(fill="x", padx=10, pady=5)
            developer_btn.bind("<Enter>", lambda e, b=developer_btn: b.config(bg="#2980b9"))
            developer_btn.bind("<Leave>", lambda e, b=developer_btn: b.config(bg="#3498db"))

        # Add exit button (for all roles)
        exit_btn = tk.Button(self.sidebar, text="إغلاق التطبيق", command=self.exit_application,
                             bg="#e74c3c", fg="white", font=GLOBAL_FONT, bd=0, padx=10, pady=5)
        exit_btn.pack(fill="x", padx=10, pady=5, side="bottom")
        exit_btn.bind("<Enter>", lambda e, b=exit_btn: b.config(bg="#c0392b"))
        exit_btn.bind("<Leave>", lambda e, b=exit_btn: b.config(bg="#e74c3c"))

        # Add datetime label
        self.datetime_label = tk.Label(self.sidebar, text="", font=GLOBAL_FONT, bg="#2c3e50", fg="white")
        self.datetime_label.pack(side="bottom", pady=10)

    def update_datetime(self):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            if hasattr(self, 'datetime_label') and self.datetime_label.winfo_exists():
                self.datetime_label.config(text=current_time)
            self.master.after(1000, self.update_datetime)
        except tk.TclError:
            print("Datetime label no longer exists. Stopping updates.")
            # Optionally, you could try to recreate the label here if needed

    def create_content(self):
        self.menu_label = tk.Label(self.content, text="اختر فئة", font=(GLOBAL_FONT[0], 24, "bold"), bg="#ecf0f1")
        self.menu_label.pack(pady=(20, 10))

        self.menu_canvas = tk.Canvas(self.content, bg="#ecf0f1", highlightthickness=0)
        self.menu_canvas.pack(side="left", fill="both", expand=True)

        self.menu_scrollbar = ttk.Scrollbar(self.content, orient="vertical", command=self.menu_canvas.yview)
        self.menu_scrollbar.pack(side="right", fill="y")

        self.menu_canvas.configure(yscrollcommand=self.menu_scrollbar.set)
        self.menu_canvas.bind('<Configure>', lambda e: self.menu_canvas.configure(scrollregion=self.menu_canvas.bbox("all")))

        self.menu_frame = tk.Frame(self.menu_canvas, bg="#ecf0f1")
        self.menu_canvas.create_window((0, 0), window=self.menu_frame, anchor="nw", width=self.content.winfo_width())
        self.content.bind('<Configure>', self.on_content_configure)

    def on_content_configure(self, event):
        self.menu_canvas.itemconfig(self.menu_canvas.find_all()[0], width=event.width)

    def create_order_frame(self):
        tk.Label(self.order_frame, text="الطلب الحالي", font=(GLOBAL_FONT[0], 18, "bold"), bg="#bdc3c7").pack(pady=20)
        
        self.order_list = tk.Frame(self.order_frame, bg="#bdc3c7")
        self.order_list.pack(fill="both", expand=True, padx=20, pady=10)

        self.total_var = tk.StringVar(value="الإجمالي: 0.00 ج.م")
        tk.Label(self.order_frame, textvariable=self.total_var, font=GLOBAL_FONT, bg="#bdc3c7").pack(pady=10)

        place_order_btn = tk.Button(self.order_frame, text="تنفيذ الطلب", command=self.place_order,
                                    bg="#e74c3c", fg="white", font=GLOBAL_FONT, bd=0, padx=10, pady=5)
        place_order_btn.pack(pady=(20, 10), padx=20, fill="x")
        place_order_btn.bind("<Enter>", lambda e, b=place_order_btn: b.config(bg="#c0392b"))
        place_order_btn.bind("<Leave>", lambda e, b=place_order_btn: b.config(bg="#e74c3c"))

        # Add Current Orders button
        current_orders_btn = tk.Button(self.order_frame, text="الطلبات الحالية", command=self.show_current_orders,
                                       bg="#3498db", fg="white", font=GLOBAL_FONT, bd=0, padx=10, pady=5)
        current_orders_btn.pack(pady=(0, 20), padx=20, fill="x")
        current_orders_btn.bind("<Enter>", lambda e, b=current_orders_btn: b.config(bg="#2980b9"))
        current_orders_btn.bind("<Leave>", lambda e, b=current_orders_btn: b.config(bg="#3498db"))

    def select_category(self, category):
        self.selected_category = category
        if self.menu_label:
            self.menu_label.config(text=category)
        
        for widget in self.menu_frame.winfo_children():
            widget.destroy()

        # Create a frame to hold the grid
        grid_frame = tk.Frame(self.menu_frame, bg="#ecf0f1")
        grid_frame.pack(expand=True, fill="both")

        row = 0
        col = 0
        items = list(self.menu[category].items())
        num_items = len(items)
        num_columns = 3

        # Calculate the number of rows needed
        num_rows = (num_items + num_columns - 1) // num_columns

        # Add empty rows at the top to center vertically
        empty_rows_top = (self.menu_frame.winfo_height() // 100 - num_rows) // 2
        for _ in range(empty_rows_top):
            tk.Frame(grid_frame, height=100, bg="#ecf0f1").grid(row=row, column=0, columnspan=num_columns)
            row += 1

        for item, price in items:
            frame = tk.Frame(grid_frame, bg="white", bd=1, relief="raised", width=200, height=150)
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            frame.grid_propagate(False)  # Prevent the frame from shrinking

            tk.Label(frame, text=item, font=(GLOBAL_FONT[0], 12, "bold"), bg="white", justify="right").pack(pady=(10, 5))
            tk.Label(frame, text=f"{price:.2f} ج.م", font=(GLOBAL_FONT[0], 10), bg="white").pack()
            
            btn_frame = tk.Frame(frame, bg="white")
            btn_frame.pack(pady=10)

            add_btn = tk.Button(btn_frame, text="إضافة", command=lambda i=item: self.add_to_order(i),
                                bg="#3498db", fg="white", font=GLOBAL_FONT, bd=0, padx=5, pady=2)
            add_btn.pack(side="left", padx=2)
            add_btn.bind("<Enter>", lambda e, b=add_btn: b.config(bg="#2980b9"))
            add_btn.bind("<Leave>", lambda e, b=add_btn: b.config(bg="#3498db"))

            if self.role == "admin":
                edit_btn = tk.Button(btn_frame, text="تعديل", command=lambda i=item: self.edit_item(category, i),
                                     bg="#f39c12", fg="white", font=GLOBAL_FONT, bd=0, padx=5, pady=2)
                edit_btn.pack(side="left", padx=2)
                edit_btn.bind("<Enter>", lambda e, b=edit_btn: b.config(bg="#d35400"))
                edit_btn.bind("<Leave>", lambda e, b=edit_btn: b.config(bg="#f39c12"))

                delete_btn = tk.Button(btn_frame, text="حذف", command=lambda i=item: self.delete_item(category, i),
                                       bg="#e74c3c", fg="white", font=GLOBAL_FONT, bd=0, padx=5, pady=2)
                delete_btn.pack(side="left", padx=2)
                delete_btn.bind("<Enter>", lambda e, b=delete_btn: b.config(bg="#c0392b"))
                delete_btn.bind("<Leave>", lambda e, b=delete_btn: b.config(bg="#e74c3c"))

            col += 1
            if col >= num_columns:
                col = 0
                row += 1

        if self.role == "admin":
            add_item_btn = tk.Button(grid_frame, text="إضافة صنف جديد", command=lambda: self.add_item(category),
                                     bg="#27ae60", fg="white", font=GLOBAL_FONT, bd=0, padx=10, pady=5)
            add_item_btn.grid(row=row+1, column=0, columnspan=num_columns, pady=20, padx=10, sticky="ew")
            add_item_btn.bind("<Enter>", lambda e, b=add_item_btn: b.config(bg="#2ecc71"))
            add_item_btn.bind("<Leave>", lambda e, b=add_item_btn: b.config(bg="#27ae60"))

        # Configure grid weights to center horizontally
        for i in range(num_columns):
            grid_frame.grid_columnconfigure(i, weight=1)

        self.menu_canvas.update_idletasks()
        self.menu_canvas.configure(scrollregion=self.menu_canvas.bbox("all"))

    def add_to_order(self, item):
        quantity = 1
        if item in self.order:
            self.order[item]['quantity'] += quantity
        else:
            self.order[item] = {'quantity': quantity, 'price': self.menu[self.selected_category][item]}
        self.update_order_display()

    def update_order_display(self):
        for widget in self.order_list.winfo_children():
            widget.destroy()

        for item, details in self.order.items():
            frame = tk.Frame(self.order_list, bg="#bdc3c7")
            frame.pack(fill="x", pady=5)
                                                
            tk.Label(frame, text=f"{item} (x{details['quantity']})", bg="#bdc3c7", font=GLOBAL_FONT, justify="right").pack(side="left")
            tk.Label(frame, text=f"{details['price'] * details['quantity']:.2f} ج.م", bg="#bdc3c7", font=GLOBAL_FONT).pack(side="right")
            
            btn_frame = tk.Frame(frame, bg="#bdc3c7")
            btn_frame.pack(side="right", padx=5)
            
            minus_btn = tk.Button(btn_frame, text="-", command=lambda i=item: self.decrease_quantity(i),
                                  bg="#e74c3c", fg="white", font=GLOBAL_FONT, width=2, bd=0)
            minus_btn.pack(side="left", padx=2)
            plus_btn = tk.Button(btn_frame, text="+", command=lambda i=item: self.increase_quantity(i),
                                 bg="#2ecc71", fg="white", font=GLOBAL_FONT, width=2, bd=0)
            plus_btn.pack(side="left", padx=2)

        self.total_var.set(f"الإجمالي: {self.calculate_total():.2f} ج.م")

    def increase_quantity(self, item):
        self.order[item]['quantity'] += 1
        self.update_order_display()

    def decrease_quantity(self, item):
        self.order[item]['quantity'] -= 1
        if self.order[item]['quantity'] <= 0:
            del self.order[item]
        self.update_order_display()

    def calculate_total(self):
        return sum(details['price'] * details['quantity'] for details in self.order.values())

    def place_order(self):
        if not self.order:
            messagebox.showerror("خطأ", "طلبك فارغ.")
            return

        # Generate a random order number
        order_number = random.randint(1000, 9999)

        # Prompt for delivery option
        delivery_option = messagebox.askyesno("خيار التوصيل", "هل تريد توصيل الطلب؟")
        delivery_location = None
        phone_number = None
        delivery_fee = 0

        if delivery_option:
            delivery_location = simpledialog.askstring("عنوان التوصيل", "أدخل عنوان التوصيل:")
            if not delivery_location:
                messagebox.showwarning("تحذير", "لم يتم إدخال عنوان التوصيل. سيتم معاملة الطلب كطلب استلام.")
            else:
                phone_number = simpledialog.askstring("رقم الهاتف", "أدخل رقم هاتف العميل:")
                delivery_fee = simpledialog.askfloat("رسوم التوصيل", "أدخل رسوم التوصيل:")

        # Icons
        whatsapp_icon = "\U0001F4AC"
        phone_icon = "\U0001F4DE"
        location_icon = "\U0001F4CD"

        # Current date and time
        current_datetime = time.strftime('%Y-%m-%d %H:%M:%S')

        order_summary = f"""
{'=' * 40}
             مطعم غنو               
{'=' * 40}

رقم الاوردر: {order_number}
التاريخ والوقت: {current_datetime}

{whatsapp_icon} هاتف: "01092392579"
{location_icon} العنوان: مفارق مشتهر امام مسجد الشهداء

{'=' * 40}
{'الصنف':<20}{'الكمية':<10}{'السعر':<10}{'الإجمالي':<10}
{'-' * 40}
"""

        order_items = []
        total = 0
        for item, details in self.order.items():
            quantity = details['quantity']
            price = details['price']
            item_total = quantity * price
            total += item_total
            order_summary += f"{item:<20}{quantity:<10}{price:<10.2f}{item_total:<10.2f}\n"
            order_items.append({
                'name': item,
                'quantity': quantity,
                'price': price,
                'total': item_total
            })

        total += delivery_fee  # Add delivery fee to total

        order_summary += f"""
{'-' * 40}
{'الإجمالي:':<30}{total:>10.2f}
{'=' * 40}

{'طريقة الاستلام:':<20}{"توصيل" if delivery_location else "استلام من المطعم"}
"""

        if delivery_location:
            order_summary += f"""{'عنوان التوصيل:':<20}{delivery_location}
{phone_icon} رقم الهاتف: {phone_number}
{'رسوم التوصيل:':<20}{delivery_fee:.2f} ج.م
"""

        order_summary += f"""
{'=' * 40}
            شكراً لزيارتكم مطعم غنو            
              نتمنى لكم وجبة شهية             
{'=' * 40}
"""

        # Print the order summary
        self.print_report(order_summary)

        # Add to current orders
        self.current_orders.append({
            'order_number': order_number,
            'items': order_items,
            'total': total,
            'delivery_location': delivery_location,
            'phone_number': phone_number,
            'delivery_fee': delivery_fee,
            'datetime': current_datetime,
            'status': 'قيد التنفيذ'  # Add this line
        })
        save_current_orders(self.current_orders)

        # Save the order to the main orders database
        save_order(order_items, total, delivery_location, order_number, phone_number, delivery_fee, 'قيد التنفيذ')

        self.clear_order()

    def print_report(self, content):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            try:
                subprocess.run(["notepad", "/p", file_path], check=True)
            except subprocess.CalledProcessError:
                messagebox.showerror("خطأ", "فشل في طباعة التقرير.")

    def print_order(self, order):
        content = self.generate_order_summary(order)
        self.print_report(content)

    def generate_order_summary(self, order):
        summary = f"""
{'=' * 40}
             مطعم غنو               
{'=' * 40}

رقم الاوردر: {order['order_number']}
التاريخ والوقت: {order['datetime']}

{'=' * 40}
{'الصنف':<20}{'الكمية':<10}{'السعر':<10}{'الإجمالي':<10}
{'-' * 40}
"""
        for item in order['items']:
            summary += f"{item['name']:<20}{item['quantity']:<10}{item['price']:<10.2f}{item['total']:<10.2f}\n"

        summary += f"""
{'-' * 40}
{'الإجمالي:':<30}{order['total']:>10.2f}
{'=' * 40}

{'طريقة الاستلام:':<20}{"توصيل" if order['delivery_location'] else "استلام من المطعم"}
"""

        if order['delivery_location']:
            summary += f"""{'عنوان التوصيل:':<20}{order['delivery_location']}
رقم الهاتف: {order['phone_number']}
{'رسوم التوصيل:':<20}{order['delivery_fee']:.2f}
"""

        summary += f"""
{'=' * 40}
            شكراً لزيارتكم مطعم غنو            
              نتمنى لكم وجبة شهية             
{'=' * 40}
"""
        return summary

    def print_order(self, order):
        content = f"رقم الطلب: {order['order_number']}\n"
        content += f"التاريخ والوقت: {order['datetime']}\n\n"
        content += "الأصناف:\n"
        for item in order['items']:
            content += f"{item['name']} x{item['quantity']} - {item['price'] * item['quantity']:.2f} ج.م\n"
        content += f"\nالإجمالي: {order['total']:.2f} ج.م\n"
        
        if order['delivery_location']:
            content += f"\nنوع الطلب: توصيل"
            content += f"\nعنوان التوصيل: {order['delivery_location']}"
            content += f"\nرقم الهاتف: {order['phone_number']}"
            content += f"\nرسوم التوصيل: {order['delivery_fee']:.2f} ج.م"
        else:
            content += f"\nنوع الطلب: استلام من المطعم"

        self.print_report(content)

    def save_order_summary(self, order_summary):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(order_summary)
            return file_path
        return None

    def print_file(self, file_path):
        if sys.platform == "win32":
            os.startfile(file_path, "print")
        else:
            subprocess.run(["lpr", file_path])

    def save_order_summary(self, order_summary):
        # Create an 'order_reports' folder if it doesn't exist
        reports_folder = os.path.join(os.getcwd(), 'order_reports')
        if not os.path.exists(reports_folder):
            os.makedirs(reports_folder)

        # Generate a unique filename based on the current timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        file_name = f"order_summary_{timestamp}.txt"
        file_path = os.path.join(reports_folder, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(order_summary)

        print(f"Order summary saved to: {file_path}")  # Debug print
        return file_path

    def print_file(self, file_path):
        try:
            subprocess.run(["notepad", "/p", file_path], check=True)
        except subprocess.CalledProcessError:
            messagebox.showerror("خطأ", "فشل في طباعة الطلب.")

    def view_reports(self):
        if self.role != "admin":
            messagebox.showerror("خطأ", "ليس لديك صلاحية لعرض التقارير")
            return
        reports_window = tk.Toplevel(self.master)
        reports_window.title("تقارير الطلبات")
        reports_window.geometry("1000x600")  # Increased width to accommodate new column
        reports_window.configure(bg="#ecf0f1")

        # Load only completed or cancelled orders
        reports = [order for order in load_orders() if order.get('status', '') in ['ناجح', 'ملغي بواسطة']]
        print(f"Loaded {len(reports)} reports")  # Debug print
        
        # Create a frame for search
        search_frame = tk.Frame(reports_window, bg="#ecf0f1")
        search_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(search_frame, text="بحث برقم الطلب:", bg="#ecf0f1", font=GLOBAL_FONT).pack(side="left", padx=(0, 10))
        search_entry = tk.Entry(search_frame, font=GLOBAL_FONT)
        search_entry.pack(side="left", expand=True, fill="x")

        def search_reports():
            search_term = search_entry.get()
            filtered_reports = [order for order in reports if str(order.get('order_number', '')) == search_term]
            populate_listbox(filtered_reports if search_term else reports)

        search_button = tk.Button(search_frame, text="بحث", command=search_reports,
                                  bg="#3498db", fg="white", font=GLOBAL_FONT, bd=0, padx=10, pady=5)
        search_button.pack(side="left", padx=(10, 0))

        # Create a frame for the listbox and scrollbar
        listbox_frame = tk.Frame(reports_window, bg="#ecf0f1")
        listbox_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create a treeview to display the reports
        columns = ("رقم الطلب", "التاريخ والوقت", "الإجمالي", "نوع الطلب", "الحالة")
        tree = ttk.Treeview(listbox_frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")

        tree.column("رقم الطلب", width=100)
        tree.column("التاريخ والوقت", width=150)
        tree.column("الإجمالي", width=100)
        tree.column("نوع الطلب", width=100)
        tree.column("الحالة", width=100)

        tree.pack(side="left", fill="both", expand=True)

        # Create a scrollbar for the treeview
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        def populate_listbox(orders):
            tree.delete(*tree.get_children())
            for order in orders:
                order_number = order.get('order_number', 'N/A')
                order_date = order.get('datetime', 'N/A')
                order_total = f"{order.get('total', 0):.2f} ج.م"
                order_type = "توصيل" if order.get('delivery_location') else "استلام"
                order_status = order.get('status', 'ناجح')  # Default to 'ناجح' if status is not set
                tree.insert("", "end", values=(order_number, order_date, order_total, order_type, order_status))

        # Initial population of the treeview
        populate_listbox(reports)

        # Create a frame for the buttons
        buttons_frame = tk.Frame(reports_window, bg="#ecf0f1")
        buttons_frame.pack(fill="x", padx=10, pady=10)

        # Create buttons for printing and closing
        print_button = tk.Button(buttons_frame, text="طباعة", command=lambda: print_selected_report(tree),
                                 bg="#2ecc71", fg="white", font=GLOBAL_FONT, bd=0, padx=10, pady=5)
        print_button.pack(side="left", padx=(0, 10))

        close_button = tk.Button(buttons_frame, text="إغلاق", command=reports_window.destroy,
                                bg="#e74c3c", fg="white", font=GLOBAL_FONT, bd=0, padx=10, pady=5)
        close_button.pack(side="left")

        def print_selected_report(tree):
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("تحذير", "لم يتم اختيار تقرير للطباعة.")
                return

            selected_report = reports[tree.index(selected_item[0])]
            order_number = selected_report.get('order_number', 'N/A')
            order_status = selected_report.get('status', 'ناجح')  # Get the status
            order_summary = f"===== ملخص الطلب =====\nمطعم غنو\n====================\n\n"
            order_summary += f"رقم الطلب: {order_number}\n"
            order_summary += f"حالة الطلب: {order_status}\n\n"  # Add status to the summary
            for item in selected_report['items']:
                if isinstance(item, dict):
                    order_summary += f"{item['name']}: {item['quantity']} x {item['price']:.2f} ج.م = {item['total']:.2f} ج.م\n"
                elif isinstance(item, str):
                    order_summary += f"{item}\n"
                else:
                    order_summary += f"{str(item)}\n"
            order_summary += f"\nالإجمالي: {selected_report['total']:.2f} ج.م"
            if selected_report.get('delivery_location'):
                order_summary += f"\nعنوان التوصيل: {selected_report['delivery_location']}"

            file_path = self.save_order_summary(order_summary)
            if file_path:
                self.print_file(file_path)

        # Print All Reports button
        def print_all_reports():
            if reports:
                content = "جميع التقارير\n\n"
                for order in reports:
                    content += f"رقم الطلب: {order.get('order_number', 'غير معروف')}\n"
                    content += f"التاريخ: {order.get('datetime', 'غير معروف')}\n"
                    content += f"الإجمالي: {order.get('total', 0):.2f} ج.م\n"
                    content += f"الحالة: {order.get('status', 'ناجح')}\n"  # Add status to the summary
                    delivery_location = order.get('delivery_location', '')
                    if delivery_location:
                        content += f"توصيل إلى: {delivery_location}\n"
                    else:
                        content += "استلام من المطعم\n"
                    content += "الأصناف:\n"
                    for item in order.get('items', []):
                        if isinstance(item, dict):
                            content += f"{item.get('name', 'غير معروف')}: {item.get('quantity', 0)} x {item.get('price', 0):.2f} ج.م = {item.get('total', 0):.2f} ج.م\n"
                        elif isinstance(item, str):
                            content += f"{item}\n"
                        else:
                            content += f"{str(item)}\n"
                    content += "\n"
                self.print_report(content)
            else:
                messagebox.showinfo("تنبيه", "لا توجد تقارير للطباعة.")

        print_all_btn = tk.Button(buttons_frame, text="طباعة جميع التقارير", command=print_all_reports,
                                  bg="#2ecc71", fg="white", font=GLOBAL_FONT,
                                  bd=0, padx=20, pady=10, activebackground="#27ae60")
        print_all_btn.pack(side="left", padx=10, expand=True, fill="x")

        # Add hover effects
        def on_enter(e):
            e.widget['background'] = e.widget.active_bg

        def on_leave(e):
            e.widget['background'] = e.widget.original_bg

        for btn in (print_button, close_button, print_all_btn):
            btn.original_bg = btn['background']
            btn.active_bg = btn['activebackground']
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

    def print_report(self, content):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            try:
                subprocess.run(["notepad", "/p", file_path], check=True)
            except subprocess.CalledProcessError:
                messagebox.showerror("خطأ", "فشل في طباعة التقرير.")

    def show_developer_info(self):
        if self.role != "admin":
            messagebox.showerror("خطأ", "ليس لديك صلاحية لعرض معلومات المطور")
            return
        info_window = tk.Toplevel(self.master)
        info_window.title("معلومات المطور")
        info_window.geometry("400x250")
        info_window.resizable(False, False)
        info_window.configure(bg="#ffffff")

        frame = tk.Frame(info_window, bg="#ffffff", padx=20, pady=20)
        frame.pack(expand=True, fill="both")

        title_label = tk.Label(frame, text="معلومات المطور", font=(GLOBAL_FONT[0], 16, "bold"), bg="#ffffff", fg="#2c3e50")
        title_label.pack(pady=(0, 10))

        info_text = "هذا النظام مصمم ومطور بواسطة\nد.أحمد الحسيني"
        info_label = tk.Label(frame, text=info_text, font=GLOBAL_FONT, bg="#ffffff", fg="#34495e", justify="center")
        info_label.pack(pady=(0, 10))

        phone_emoji = "📞"  # Unicode phone emoji
        phone_text = f"{phone_emoji} 01090562241"
        phone_label = tk.Label(frame, text=phone_text, font=GLOBAL_FONT, bg="#ffffff", fg="#3498db")
        phone_label.pack(pady=(0, 10))

        # Add Revenue Management button
        revenue_btn = tk.Button(frame, text="إدارة الإيرادات", command=self.open_revenue_management,
                                bg="#3498db", fg="white", font=GLOBAL_FONT, bd=0, padx=10, pady=5)
        revenue_btn.pack(pady=10)
        revenue_btn.bind("<Enter>", lambda e: revenue_btn.config(bg="#2980b9"))
        revenue_btn.bind("<Leave>", lambda e: revenue_btn.config(bg="#3498db"))

    def open_revenue_management(self):
        if self.role != "admin":
            messagebox.showerror("خطأ", "ليس لديك صلاحية لإدارة الإيرادات")
            return
        revenue_window = tk.Toplevel(self.master)
        revenue_app = ModernRevenueManagementUI(revenue_window)

    def exit_application(self):
        if messagebox.askyesno("تأكيد الخروج", "هل أنت متأكد من إغلاق التطبيق؟"):
            save_current_orders(self.current_orders)  # Save current orders before closing
            self.master.destroy()

    def edit_item(self, category, item):
        current_price = self.menu[category][item]
        new_price = simpledialog.askfloat("تعديل السعر", f"أدخل السعر الجديد لـ {item}:", initialvalue=current_price)
        if new_price is not None:
            self.menu[category][item] = new_price
            self.select_category(category)  # Refresh the display
            save_menu(self.menu)  # Save the updated menu
            messagebox.showinfo("نجاح", f"تم تحديث سعر {item} إلى {new_price:.2f} ج.م")

    def delete_item(self, category, item):
        if messagebox.askyesno("تأكيد الحذف", f"هل أنت متأكد من حذف {item}؟"):
            del self.menu[category][item]
            self.select_category(category)  # Refresh the display
            save_menu(self.menu)  # Save the updated menu
            messagebox.showinfo("نجاح", f"تم حذف {item} من القائمة")

    def add_item(self, category):
        new_item = simpledialog.askstring("إضافة صنف", "أدخل اسم الصنف الجديد:")
        if new_item:
            if new_item in self.menu[category]:
                messagebox.showerror("خطأ", "هذا الصنف موجود بالفعل")
                return
            new_price = simpledialog.askfloat("إضافة صنف", f"أدخل سعر {new_item}:")
            if new_price is not None:
                self.menu[category][new_item] = new_price
                self.select_category(category)  # Refresh the display
                save_menu(self.menu)  # Save the updated menu
                messagebox.showinfo("نجاح", f"تمت إضافة {new_item} بسعر {new_price:.2f} ج.م")

    def add_category(self):
        new_category = simpledialog.askstring("إضافة فئة", "أدخل اسم الفئة الجديدة:")
        if new_category:
            if new_category not in self.menu:
                self.menu[new_category] = {}
                self.refresh_categories()  # Use refresh_categories instead of create_sidebar
                messagebox.showinfo("نجاح", f"تمت إضافة الفئة {new_category} بنجاح")
                save_menu(self.menu)  # Save the updated menu
            else:
                messagebox.showerror("خطأ", "هذه الفئة موجودة بالفعل")

    def edit_category(self):
        categories = list(self.menu.keys())
        if not categories:
            messagebox.showerror("خطأ", "لا توجد فئات للتعديل")
            return

        category_to_edit = simpledialog.askstring("تعديل فئة", "اختر الفئة للتعديل:", initialvalue=categories[0])
        if category_to_edit not in categories:
            messagebox.showerror("خطأ", "الفئة غير موجودة")
            return

        new_category_name = simpledialog.askstring("تعديل فئة", f"أدخل الاسم الجديد لـ '{category_to_edit}':")
        if new_category_name and new_category_name != category_to_edit:
            self.menu[new_category_name] = self.menu.pop(category_to_edit)
            self.refresh_categories()  # Use refresh_categories instead of create_sidebar
            messagebox.showinfo("نجاح", f"تم تغيير اسم الفئة من '{category_to_edit}' إلى '{new_category_name}'")
            save_menu(self.menu)  # Save the updated menu
        elif new_category_name == category_to_edit:
            messagebox.showinfo("تنبيه", "لم يتم إجراء أي تغيير")

    def refresh_categories(self):
        # Remove category buttons and the "الفئات" label
        for widget in self.sidebar.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget('text') not in ["إضافة فئة", "تعديل فئة", "عرض التقارير", "مطور التطبيق", "إغلاق التطبيق"]:
                widget.destroy()
            elif isinstance(widget, tk.Label) and widget.cget('text') == "الفئات":
                widget.destroy()

        # Recreate "الفئات" label and category buttons
        tk.Label(self.sidebar, text="الفئات", font=(GLOBAL_FONT[0], 18, "bold"), bg="#2c3e50", fg="white").pack(pady=20)
        for category in self.menu.keys():
            btn = tk.Button(self.sidebar, text=category, command=lambda c=category: self.select_category(c),
                            bg="#34495e", fg="white", font=GLOBAL_FONT, bd=0, padx=10, pady=5, justify="right")
            btn.pack(fill="x", padx=10, pady=5)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#3498db"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#34495e"))

        # Ensure admin buttons are at the bottom
        admin_buttons = [widget for widget in self.sidebar.winfo_children() if isinstance(widget, tk.Button) and widget.cget('text') in ["إضافة فئة", "تعديل فئة", "عرض التقارير", "مطور التطبيق"]]
        exit_button = next((widget for widget in self.sidebar.winfo_children() if isinstance(widget, tk.Button) and widget.cget('text') == "إغلاق التطبيق"), None)

        for btn in admin_buttons:
            btn.pack_forget()
            btn.pack(fill="x", padx=10, pady=5)

        if exit_button:
            exit_button.pack_forget()
            exit_button.pack(fill="x", padx=10, pady=5, side="bottom")

        # Ensure datetime label is at the bottom
        if hasattr(self, 'datetime_label') and self.datetime_label.winfo_exists():
            self.datetime_label.pack_forget()
            self.datetime_label.pack(side="bottom", pady=10)

        # Update the view
        self.sidebar.update()

    def show_current_orders(self):
        if self.current_orders_window and self.current_orders_window.winfo_exists():
            self.current_orders_window.lift()
            self.refresh_current_orders()
            return

        self.current_orders_window = tk.Toplevel(self.master)
        self.current_orders_window.title("الطلبات الحالية")
        self.current_orders_window.geometry("1200x600")
        self.current_orders_window.configure(bg="#ecf0f1")

        # Create a main frame
        main_frame = tk.Frame(self.current_orders_window, bg="#ecf0f1")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(main_frame, text="الطلبات الحالية", font=(GLOBAL_FONT[0], 24, "bold"), bg="#ecf0f1", fg="#2c3e50")
        title_label.pack(pady=(0, 20))

        # Create a frame for the treeview
        tree_frame = tk.Frame(main_frame, bg="#ffffff")
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Create the treeview with a modern style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#ffffff", foreground="#2c3e50", rowheight=25, fieldbackground="#ffffff")
        style.map('Treeview', background=[('selected', '#3498db')])
        style.configure("Treeview.Heading", background="#3498db", foreground="white", font=(GLOBAL_FONT[0], 12, "bold"))

        columns = ("رقم الطلب", "الأصناف", "الإجمالي", "نوع الطلب", "حالة الطلب")
        self.current_orders_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', style="Treeview")

        # Define headings
        for col in columns:
            self.current_orders_tree.heading(col, text=col)
            self.current_orders_tree.column(col, width=100, anchor="center")

        # Adjust column widths
        self.current_orders_tree.column("رقم الطلب", width=100)
        self.current_orders_tree.column("الأصناف", width=400)
        self.current_orders_tree.column("الإجمالي", width=150)
        self.current_orders_tree.column("نوع الطلب", width=150)
        self.current_orders_tree.column("حالة الطلب", width=150)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.current_orders_tree.yview)
        self.current_orders_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.current_orders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.refresh_current_orders()

        # Add buttons
        button_frame = tk.Frame(main_frame, bg="#ecf0f1")
        button_frame.pack(pady=20)

        finish_btn = tk.Button(button_frame, text="إنهاء الطلب", command=self.finish_order,
                               bg="#2ecc71", fg="white", font=GLOBAL_FONT, bd=0, padx=20, pady=10)
        finish_btn.pack(side=tk.LEFT, padx=10)

        cancel_btn = tk.Button(button_frame, text="تحديث كملغي", command=self.update_order_as_cancelled,
                               bg="#e74c3c", fg="white", font=GLOBAL_FONT, bd=0, padx=20, pady=10)
        cancel_btn.pack(side=tk.LEFT, padx=10)

        close_btn = tk.Button(button_frame, text="إغلاق", command=self.current_orders_window.destroy,
                              bg="#34495e", fg="white", font=GLOBAL_FONT, bd=0, padx=20, pady=10)
        close_btn.pack(side=tk.LEFT, padx=10)

        # Add owner removal button (only for admin)
        if self.role == "admin":
            owner_remove_btn = tk.Button(button_frame, text="حذف الطلب (المالك)", command=self.owner_remove_order,
                                         bg="#8e44ad", fg="white", font=GLOBAL_FONT, bd=0, padx=20, pady=10)
            owner_remove_btn.pack(side=tk.LEFT, padx=10)

        # Add hover effects
        for btn in (finish_btn, cancel_btn, close_btn):
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2c3e50"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=b['background']))

        if self.role == "admin":
            owner_remove_btn.bind("<Enter>", lambda e: owner_remove_btn.config(bg="#6c3483"))
            owner_remove_btn.bind("<Leave>", lambda e: owner_remove_btn.config(bg="#8e44ad"))

    def refresh_current_orders(self):
        if not self.current_orders_tree:
            return
        self.current_orders_tree.delete(*self.current_orders_tree.get_children())
        for order in self.current_orders:
            items_str = ", ".join([f"{item['name']} (x{item['quantity']})" for item in order['items']])
            order_type = "توصيل" if order['delivery_location'] else "استلام"
            order_status = order.get('status', 'قيد التنفيذ')
            self.current_orders_tree.insert("", tk.END, values=(order['order_number'], items_str, f"{order['total']:.2f} ج.م", order_type, order_status))

    def update_order_as_cancelled(self):
        if not self.current_orders_tree:
            return
        selected_item = self.current_orders_tree.selection()
        if not selected_item:
            messagebox.showwarning("تحذير", "الرجاء اختيار طلب لتحديثه كملغي")
            return

        order_number = self.current_orders_tree.item(selected_item)['values'][0]
        order = next((o for o in self.current_orders if str(o['order_number']) == str(order_number)), None)
        
        if order:
            if order['status'].startswith('ملغي بواسطة'):
                messagebox.showwarning("تحذير", f"الطلب رقم {order_number} ملغي بالفعل")
                return

            if messagebox.askyesno("تأكيد", f"هل أنت متأكد من تحديث الطلب رقم {order_number} كملغي؟"):
                cancel_reason = f"ملغي بواسطة {self.username}"
                order['status'] = cancel_reason
                # Save the cancelled order to the main orders database
                save_order(order['items'], order['total'], order['delivery_location'], order['order_number'], 
                           order['phone_number'], order['delivery_fee'], cancel_reason)
                save_current_orders(self.current_orders)  # Save after updating order
                messagebox.showinfo("نجاح", f"تم تحديث الطلب رقم {order_number} كملغي")
                
                # Update the tree item to show the new status
                current_values = list(self.current_orders_tree.item(selected_item)['values'])
                current_values[-1] = cancel_reason  # Update the last column (status)
                self.current_orders_tree.item(selected_item, values=current_values)
        else:
            messagebox.showerror("خطأ", "لم يتم العثور على الطلب")

    def finish_order(self):
        if not self.current_orders_tree:
            return
        selected_item = self.current_orders_tree.selection()
        if not selected_item:
            messagebox.showwarning("تحذير", "الرجاء اختيار طلب لإنهائه")
            return

        order_number = self.current_orders_tree.item(selected_item)['values'][0]
        order = next((o for o in self.current_orders if str(o['order_number']) == str(order_number)), None)
        if order:
            if order['status'].startswith('ملغي بواسطة'):
                messagebox.showwarning("تحذير", f"لا يمكن إنهاء الطلب رقم {order_number} لأنه ملغي")
                return
            
            # Update order status to 'ناجح'
            order['status'] = 'ناجح'
            
            # Save the order to the main orders database
            save_order(order['items'], order['total'], order['delivery_location'], order['order_number'], 
                       order['phone_number'], order['delivery_fee'], 'ناجح')
            
            # Remove from current orders
            self.current_orders = [o for o in self.current_orders if str(o['order_number']) != str(order_number)]
            save_current_orders(self.current_orders)  # Save after removing order
            messagebox.showinfo("نجاح", f"تم إنهاء الطلب رقم {order_number}")
            self.current_orders_tree.delete(selected_item)
            self.refresh_current_orders()
        else:
            messagebox.showerror("خطأ", "لم يتم العثور على الطلب")

    def owner_remove_order(self):
        if not self.current_orders_tree:
            return
        selected_item = self.current_orders_tree.selection()
        if not selected_item:
            messagebox.showwarning("تحذير", "الرجاء اختيار طلب لحذفه")
            return

        password = simpledialog.askstring("كلمة المرور", "أدخل كلمة مرور المالك:", show='*')
        if password != "123":
            messagebox.showerror("خطأ", "كلمة المرور غير صحيحة")
            return

        order_number = self.current_orders_tree.item(selected_item)['values'][0]
        order = next((o for o in self.current_orders if str(o['order_number']) == str(order_number)), None)
        
        if order:
            if messagebox.askyesno("تأكيد", f"هل أنت متأكد من حذف الطلب رقم {order_number}؟"):
                # Remove from current orders
                self.current_orders = [o for o in self.current_orders if str(o['order_number']) != str(order_number)]
                save_current_orders(self.current_orders)  # Save after removing order
                messagebox.showinfo("نجاح", f"تم حذف الطلب رقم {order_number}")
                self.current_orders_tree.delete(selected_item)
                self.refresh_current_orders()
        else:
            messagebox.showerror("خطأ", "لم يتم العثور على الطلب")
        
    def on_closing(self):
        if messagebox.askyesno("تأكيد الخروج", "هل أنت متأكد أنك تريد إغلاق التطبيق؟"):
            save_current_orders(self.current_orders)  # Save current orders before closing
            self.master.destroy()

    def finish_order(self):
        if not self.current_orders_tree:
            return
        selected_item = self.current_orders_tree.selection()
        if not selected_item:
            messagebox.showwarning("تحذير", "الرجاء اختيار طلب لإنهائه")
            return

        order_number = self.current_orders_tree.item(selected_item)['values'][0]
        order = next((o for o in self.current_orders if str(o['order_number']) == str(order_number)), None)
        if order:
            if order['status'].startswith('ملغي بواسطة'):
                messagebox.showerror("خطأ", "لا يمكن إنهاء طلب ملغي إلا بواسطة المدير")
                return
            
            # Update order status to 'ناجح'
            order['status'] = 'ناجح'
            
            # Save the order to the main orders database
            save_order(order['items'], order['total'], order['delivery_location'], order['order_number'], 
                       order['phone_number'], order['delivery_fee'], 'ناجح')
            
            # Remove from current orders
            self.current_orders = [o for o in self.current_orders if str(o['order_number']) != str(order_number)]
            save_current_orders(self.current_orders)  # Save after removing order
            messagebox.showinfo("نجاح", f"تم إنهاء الطلب رقم {order_number}")
            self.current_orders_tree.delete(selected_item)
            self.refresh_current_orders()
        else:
            messagebox.showerror("خطأ", "لم يتم العثور على الطلب")

def start_pos_system(username, role):
    root = tk.Tk()
    app = ModernFoodOrderGUI(root, username, role)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    start_login(start_pos_system)


