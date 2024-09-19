import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import date, timedelta, datetime
import time
import json
import os

# Constants
GLOBAL_FONT = ("Tajawal", 12)
BG_COLOR = "#f0f0f0"
SIDEBAR_COLOR = "#2c3e50"
CONTENT_COLOR = "#ecf0f1"
BUTTON_COLOR = "#3498db"
BUTTON_ACTIVE_COLOR = "#2980b9"

class ModernRevenueManagementUI:
    def __init__(self, master):
        self.master = master
        self.master.title("نظام إدارة الإيرادات")
        self.master.geometry("1366x768")
        self.master.configure(bg=BG_COLOR)

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_styles()

        self.data_file = "revenue_management.json"
        self.load_data()

        self.create_widgets()

    def configure_styles(self):
        self.style.configure("TFrame", background=CONTENT_COLOR)
        self.style.configure("TLabel", background=CONTENT_COLOR, font=GLOBAL_FONT)
        self.style.configure("TEntry", font=GLOBAL_FONT)
        self.style.configure("TButton", font=GLOBAL_FONT, background=BUTTON_COLOR, foreground="white")
        self.style.map("TButton", background=[('active', BUTTON_ACTIVE_COLOR)])
        self.style.configure("Treeview", font=GLOBAL_FONT, rowheight=25)
        self.style.configure("Treeview.Heading", font=GLOBAL_FONT)

    def create_widgets(self):
        self.create_sidebar()
        self.create_content()

    def create_sidebar(self):
        sidebar = tk.Frame(self.master, bg=SIDEBAR_COLOR, width=250)
        sidebar.pack(side="left", fill="y")

        title = tk.Label(sidebar, text="إدارة الإيرادات", font=(GLOBAL_FONT[0], 18, "bold"), bg=SIDEBAR_COLOR, fg="white")
        title.pack(pady=20)

        buttons = [
            ("الإيرادات اليومية", self.show_daily_revenue),
            ("تكاليف الموردين", self.show_supplier_costs),
            ("التقارير", self.show_reports),
            ("إغلاق التطبيق", self.exit_application)
        ]

        for text, command in buttons:
            btn = tk.Button(sidebar, text=text, command=command, bg=SIDEBAR_COLOR, fg="white",
                            font=GLOBAL_FONT, bd=0, padx=10, pady=5, anchor="w", width=25)
            btn.pack(fill="x", padx=10, pady=5)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#34495e"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=SIDEBAR_COLOR))

        self.datetime_label = tk.Label(sidebar, text="", font=GLOBAL_FONT, bg=SIDEBAR_COLOR, fg="white")
        self.datetime_label.pack(side="bottom", pady=10)
        self.update_datetime()

    def create_content(self):
        self.content_frame = ttk.Frame(self.master)
        self.content_frame.pack(side="left", fill="both", expand=True)

        self.show_daily_revenue()  # Show daily revenue by default

    def update_datetime(self):
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        self.datetime_label.config(text=current_time)
        self.master.after(1000, self.update_datetime)

    def show_daily_revenue(self):
        self.clear_content()
        frame = ttk.Frame(self.content_frame)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ttk.Label(frame, text="إضافة إيراد يومي", font=(GLOBAL_FONT[0], 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(frame, text="التاريخ:").grid(row=1, column=0, sticky="e", pady=5)
        self.date_label = ttk.Label(frame, text=date.today().strftime("%Y-%m-%d"), font=GLOBAL_FONT)
        self.date_label.grid(row=1, column=1, sticky="w", pady=5)

        ttk.Label(frame, text="الإيراد:").grid(row=2, column=0, sticky="e", pady=5)
        self.revenue_entry = ttk.Entry(frame)
        self.revenue_entry.grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Label(frame, text="نوع الشفت:").grid(row=3, column=0, sticky="e", pady=5)
        self.shift_type = tk.StringVar(value="شفت النهار")
        self.shift_type_combo = ttk.Combobox(frame, textvariable=self.shift_type, values=["شفت النهار", "شفت الليل"], state="readonly")
        self.shift_type_combo.grid(row=3, column=1, sticky="ew", pady=5)

        add_button = ttk.Button(frame, text="إضافة الإيراد", command=self.add_daily_revenue)
        add_button.grid(row=4, column=1, sticky="e", pady=10)

        # Add table
        self.daily_revenue_table = ttk.Treeview(frame, columns=("date", "time", "revenue", "shift_type"), show="headings")
        self.daily_revenue_table.heading("date", text="التاريخ")
        self.daily_revenue_table.heading("time", text="الوقت")
        self.daily_revenue_table.heading("revenue", text="الإيراد")
        self.daily_revenue_table.heading("shift_type", text="نوع الشفت")
        self.daily_revenue_table.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=10)

        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(5, weight=1)

        self.update_daily_revenue_table()

        # Add edit and delete buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)

        edit_button = ttk.Button(button_frame, text="تعديل", command=self.edit_daily_revenue)
        edit_button.pack(side="left", padx=5)

        delete_button = ttk.Button(button_frame, text="حذف", command=self.delete_daily_revenue)
        delete_button.pack(side="left", padx=5)

    def show_supplier_costs(self):
        self.clear_content()
        frame = ttk.Frame(self.content_frame)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ttk.Label(frame, text="إضافة تكلفة مورد", font=(GLOBAL_FONT[0], 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(frame, text="التاريخ:").grid(row=1, column=0, sticky="e", pady=5)
        self.supplier_date_label = ttk.Label(frame, text=date.today().strftime("%Y-%m-%d"), font=GLOBAL_FONT)
        self.supplier_date_label.grid(row=1, column=1, sticky="w", pady=5)

        ttk.Label(frame, text="اسم المورد:").grid(row=2, column=0, sticky="e", pady=5)
        self.supplier_name_entry = ttk.Entry(frame)
        self.supplier_name_entry.grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Label(frame, text="نوع البضاعة:").grid(row=3, column=0, sticky="e", pady=5)
        self.goods_type_entry = ttk.Entry(frame)
        self.goods_type_entry.grid(row=3, column=1, sticky="ew", pady=5)

        ttk.Label(frame, text="ملاحظات:").grid(row=4, column=0, sticky="e", pady=5)
        self.notes_entry = ttk.Entry(frame)
        self.notes_entry.grid(row=4, column=1, sticky="ew", pady=5)

        ttk.Label(frame, text="التكلفة:").grid(row=5, column=0, sticky="e", pady=5)
        self.cost_entry = ttk.Entry(frame)
        self.cost_entry.grid(row=5, column=1, sticky="ew", pady=5)

        # Modern style checkboxes with consistent background
        self.payment_type = tk.StringVar(value="كاش")
        checkbox_frame = ttk.Frame(frame)
        checkbox_frame.grid(row=6, column=0, columnspan=2, sticky="w", pady=5)

        style = ttk.Style()
        style.configure("Transparent.TCheckbutton", font=GLOBAL_FONT)

        cash_checkbox = ttk.Checkbutton(checkbox_frame, text="كاش", variable=self.payment_type, 
                                        onvalue="كاش", offvalue="آجل", style="Transparent.TCheckbutton",
                                        command=lambda: self.update_checkboxes("كاش"))
        cash_checkbox.pack(side="left", padx=(0, 10))

        credit_checkbox = ttk.Checkbutton(checkbox_frame, text="آجل", variable=self.payment_type, 
                                          onvalue="آجل", offvalue="كاش", style="Transparent.TCheckbutton",
                                          command=lambda: self.update_checkboxes("آجل"))
        credit_checkbox.pack(side="left")

        add_button = ttk.Button(frame, text="إضافة التكلفة", command=self.add_supplier_cost)
        add_button.grid(row=7, column=1, sticky="e", pady=10)

        # Create a frame to hold the table and scrollbars
        table_frame = ttk.Frame(frame)
        table_frame.grid(row=8, column=0, columnspan=2, sticky="nsew", pady=10)

        # Add table with horizontal and vertical scrollbars
        self.supplier_costs_table = ttk.Treeview(table_frame, columns=("date", "time", "supplier", "goods_type", "notes", "cost", "payment_type"), show="headings")
        self.supplier_costs_table.heading("date", text="التاريخ")
        self.supplier_costs_table.heading("time", text="الوقت")
        self.supplier_costs_table.heading("supplier", text="المورد")
        self.supplier_costs_table.heading("goods_type", text="نوع البضاعة")
        self.supplier_costs_table.heading("notes", text="ملاحظات")
        self.supplier_costs_table.heading("cost", text="التكلفة")
        self.supplier_costs_table.heading("payment_type", text="نوع الدفع")

        # Set column widths and center text
        for col in self.supplier_costs_table["columns"]:
            self.supplier_costs_table.column(col, width=100, minwidth=100, anchor="center")

        # Configure tags for centered text
        self.supplier_costs_table.tag_configure("centered", anchor="center")

        # Add vertical scrollbar
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.supplier_costs_table.yview)
        v_scrollbar.pack(side="right", fill="y")
        self.supplier_costs_table.configure(yscrollcommand=v_scrollbar.set)

        # Add horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.supplier_costs_table.xview)
        h_scrollbar.pack(side="bottom", fill="x")
        self.supplier_costs_table.configure(xscrollcommand=h_scrollbar.set)

        self.supplier_costs_table.pack(side="left", fill="both", expand=True)

        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(8, weight=1)

        self.update_supplier_costs_table()

        # Add edit and delete buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=10)

        edit_button = ttk.Button(button_frame, text="تعديل", command=self.edit_supplier_cost)
        edit_button.pack(side="left", padx=5)

        delete_button = ttk.Button(button_frame, text="حذف", command=self.delete_supplier_cost)
        delete_button.pack(side="left", padx=5)

    def update_checkboxes(self, selected):
        self.payment_type.set(selected)

    def show_reports(self):
        self.clear_content()
        frame = ttk.Frame(self.content_frame)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ttk.Label(frame, text="التقارير", font=(GLOBAL_FONT[0], 16, "bold")).pack(pady=10)

        report_types = [
            ("تقرير الإيرادات اليومية", self.generate_daily_revenue_report),
            ("تقرير تكاليف الموردين", self.generate_supplier_costs_report),
            ("تقرير الإيرادات الشهرية", self.generate_monthly_revenue_report)
        ]

        for text, command in report_types:
            btn = ttk.Button(frame, text=text, command=command)
            btn.pack(pady=5, fill="x")

        # Create Treeview for report display
        self.report_tree = ttk.Treeview(frame, show="headings", selectmode="none")
        self.report_tree.pack(pady=10, fill="both", expand=True)

        # Add scrollbar to the Treeview
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.report_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.report_tree.configure(yscrollcommand=scrollbar.set)

        # Add print button
        print_button = ttk.Button(frame, text="طباعة التقرير", command=self.print_report)
        print_button.pack(pady=10)

    def print_report(self):
        if not self.report_tree.get_children():
            messagebox.showwarning("تحذير", "لا يوجد تقرير لطباعته. الرجاء توليد تقرير أولاً.")
            return

        report_content = "تقرير\n\n"
        
        headers = [self.report_tree.heading(col)["text"] for col in self.report_tree["columns"]]

        if self.current_report_type == "monthly":
            report_content += "تقرير الإيرادات الشهرية\n\n"
        elif self.current_report_type == "daily":
            report_content += "تقرير الإيرادات اليومية\n\n"
        elif self.current_report_type == "supplier":
            report_content += "تقرير تكاليف الموردين\n\n"

        for item in self.report_tree.get_children():
            values = self.report_tree.item(item)["values"]
            for header, value in zip(headers, values):
                report_content += f"{header}: {value}\n"
            report_content += "-" * 40 + "\n"  # Separator between entries

        # Print the report
        print_window = tk.Toplevel(self.master)
        print_window.title("طباعة التقرير")
        
        text_widget = tk.Text(print_window, wrap=tk.WORD, font=("Arial", 14))
        text_widget.insert(tk.END, report_content)
        text_widget.pack(expand=True, fill="both")

        def print_and_close():
            self.print_file(report_content)
            print_window.destroy()

        print_button = ttk.Button(print_window, text="طباعة", command=print_and_close)
        print_button.pack(pady=10)

    def print_file(self, content):
        file_path = "temp_report.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        os.startfile(file_path, "print")

    def generate_monthly_revenue_report(self):
        # Clear previous data
        for col in self.report_tree["columns"]:
            self.report_tree.heading(col, text="")
        self.report_tree.delete(*self.report_tree.get_children())

        # Set up columns
        columns = ("الشهر", "الايراد", "التكاليف", "صافي الربح")
        self.report_tree["columns"] = columns
        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, anchor="center", width=100)

        monthly_data = {}
        
        for entry in self.daily_revenue_data:
            month = entry[0].strftime("%Y-%m")
            if month not in monthly_data:
                monthly_data[month] = {"revenue": 0, "costs": 0}
            monthly_data[month]["revenue"] += entry[2]
        
        for entry in self.supplier_costs_data:
            month = entry[0].strftime("%Y-%m")
            if month not in monthly_data:
                monthly_data[month] = {"revenue": 0, "costs": 0}
            try:
                monthly_data[month]["costs"] += float(entry[5])  # Use index 5 for cost and convert to float
            except ValueError:
                print(f"Invalid cost value: {entry[5]}")
        
        total_revenue = 0
        total_costs = 0
        total_profit = 0
        
        for month, data in sorted(monthly_data.items()):
            revenue = data["revenue"]
            costs = data["costs"]
            profit = revenue - costs
            self.report_tree.insert("", "end", values=(month, f"{revenue:.2f}", f"{costs:.2f}", f"{profit:.2f}"))
            total_revenue += revenue
            total_costs += costs
            total_profit += profit
        
        # Add totals row
        self.report_tree.insert("", "end", values=("الإجمالي", f"{total_revenue:.2f}", f"{total_costs:.2f}", f"{total_profit:.2f}"))

        self.current_report_type = "monthly"

    def generate_daily_revenue_report(self):
        # Clear previous data
        for col in self.report_tree["columns"]:
            self.report_tree.heading(col, text="")
        self.report_tree.delete(*self.report_tree.get_children())

        # Set up columns
        columns = ("التاريخ", "الوقت", "الإيراد")
        self.report_tree["columns"] = columns
        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, anchor="center", width=100)

        total_revenue = 0
        for entry in sorted(self.daily_revenue_data, key=lambda x: (x[0], x[1])):
            self.report_tree.insert("", "end", values=(entry[0].strftime("%Y-%m-%d"), entry[1], f"{entry[2]:.2f}"))
            total_revenue += entry[2]
        
        self.report_tree.insert("", "end", values=("إجمالي الإيرادات", "", f"{total_revenue:.2f}"))

        self.current_report_type = "daily"

    def generate_supplier_costs_report(self):
        # Clear previous data
        for col in self.report_tree["columns"]:
            self.report_tree.heading(col, text="")
        self.report_tree.delete(*self.report_tree.get_children())

        # Set up columns to match the supplier costs table
        columns = ("التاريخ", "الوقت", "المورد", "نوع البضاعة", "ملاحظات", "التكلفة", "نوع الدفع")
        self.report_tree["columns"] = columns
        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, anchor="center", width=100)

        total_cost = 0
        for entry in sorted(self.supplier_costs_data, key=lambda x: (x[0], x[1])):
            try:
                cost = float(entry[5])  # Use index 5 for cost and convert to float
                formatted_entry = list(entry)
                formatted_entry[0] = formatted_entry[0].strftime("%Y-%m-%d")
                formatted_entry[5] = f"{cost:.2f}"  # Format the cost as a float with 2 decimal places
                self.report_tree.insert("", "end", values=formatted_entry)
                total_cost += cost
            except ValueError:
                print(f"Invalid cost value: {entry[5]}")
                formatted_entry = list(entry)
                formatted_entry[0] = formatted_entry[0].strftime("%Y-%m-%d")
                formatted_entry[5] = "Invalid Cost"
                self.report_tree.insert("", "end", values=formatted_entry)

        self.report_tree.insert("", "end", values=("إجمالي التكاليف", "", "", "", "", f"{total_cost:.2f}", ""))

        self.current_report_type = "supplier"

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def add_daily_revenue(self):
        revenue_str = self.revenue_entry.get()
        shift_type = self.shift_type.get()
        
        try:
            revenue = float(revenue_str)
            entry_date = date.today()
            entry_time = datetime.now().strftime("%H:%M:%S")
            
            # Check if an entry for the same shift type already exists for today
            existing_entry = next((entry for entry in self.daily_revenue_data 
                                   if entry[0] == entry_date and entry[3] == shift_type), None)
            
            if existing_entry:
                messagebox.showerror("خطأ", "عفوا لا يمكنك اضافة أكثر من إيراد لنفس الشفت في نفس اليوم")
                return
            
            self.daily_revenue_data.append((entry_date, entry_time, revenue, shift_type))
            self.update_daily_revenue_table()
            self.save_data()  # Save data after adding new entry
            
            self.revenue_entry.delete(0, tk.END)
            messagebox.showinfo("نجاح", "تمت إضافة الإيراد اليومي بنجاح")
        except ValueError:
            messagebox.showerror("خطأ", "الرجاء إدخال قيمة صحيحة للإيراد")

    def update_daily_revenue_table(self):
        self.daily_revenue_table.delete(*self.daily_revenue_table.get_children())
        for entry in sorted(self.daily_revenue_data, key=lambda x: (x[0], x[1]), reverse=True):
            self.daily_revenue_table.insert("", "end", values=(entry[0].strftime("%Y-%m-%d"), entry[1], f"{entry[2]:.2f}", entry[3]))

    def add_supplier_cost(self):
        supplier = self.supplier_name_entry.get()
        goods_type = self.goods_type_entry.get()
        notes = self.notes_entry.get()
        cost_str = self.cost_entry.get()
        payment_type = self.payment_type.get()
        
        try:
            cost = float(cost_str)
            entry_date = date.today()
            entry_time = datetime.now().strftime("%H:%M:%S")
            
            self.supplier_costs_data.append((entry_date, entry_time, supplier, goods_type, notes, cost, payment_type))
            self.update_supplier_costs_table()
            self.save_data()  # Save data after adding new entry
            
            self.supplier_name_entry.delete(0, tk.END)
            self.goods_type_entry.delete(0, tk.END)
            self.notes_entry.delete(0, tk.END)
            self.cost_entry.delete(0, tk.END)
            messagebox.showinfo("نجاح", "تمت إضافة تكلفة المورد بنجاح")
        except ValueError:
            messagebox.showerror("خطأ", "الرجاء إدخال قيمة صحيحة للتكلفة")

    def update_supplier_costs_table(self):
        self.supplier_costs_table.delete(*self.supplier_costs_table.get_children())
        for entry in sorted(self.supplier_costs_data, key=lambda x: (x[0], x[1]), reverse=True):
            formatted_entry = list(entry)
            formatted_entry[0] = formatted_entry[0].strftime("%Y-%m-%d")
            formatted_entry[5] = f"{float(entry[5]):.2f}"  # Format the cost as a float with 2 decimal places
            self.supplier_costs_table.insert("", "end", values=formatted_entry, tags=("centered",))

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.daily_revenue_data = [
                    (datetime.strptime(item[0], "%Y-%m-%d").date(), item[1], item[2], item[3])
                    for item in data.get('daily_revenue', [])
                ]
                self.supplier_costs_data = [
                    (datetime.strptime(item[0], "%Y-%m-%d").date(), item[1], item[2], item[3], item[4], item[5], item[6])
                    for item in data.get('supplier_costs', [])
                ]
        else:
            self.daily_revenue_data = []
            self.supplier_costs_data = []

    def save_data(self):
        data = {
            'daily_revenue': [
                [item[0].strftime("%Y-%m-%d"), item[1], item[2], item[3]]
                for item in self.daily_revenue_data
            ],
            'supplier_costs': [
                [item[0].strftime("%Y-%m-%d"), item[1], item[2], item[3], item[4], item[5], item[6]]
                for item in self.supplier_costs_data
            ]
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    def exit_application(self):
        if messagebox.askyesno("إغلاق", "هل أنت متأكد من رغبتك في إغلاق التطبيق؟"):
            self.save_data()  # Save data before closing the application
            self.master.destroy()

    def edit_daily_revenue(self):
        selected_item = self.daily_revenue_table.selection()
        if not selected_item:
            messagebox.showwarning("تحذير", "الرجاء تحديد عنصر للتعديل")
            return

        item = self.daily_revenue_table.item(selected_item)
        date, time, revenue, shift_type = item['values']

        # Create a dialog for editing
        dialog = tk.Toplevel(self.master)
        dialog.title("تعديل الإيراد اليومي")

        ttk.Label(dialog, text="الإيراد:").grid(row=0, column=0, sticky="e", pady=5)
        revenue_entry = ttk.Entry(dialog)
        revenue_entry.insert(0, revenue)
        revenue_entry.grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(dialog, text="نوع الشفت:").grid(row=1, column=0, sticky="e", pady=5)
        shift_type_var = tk.StringVar(value=shift_type)
        shift_type_combo = ttk.Combobox(dialog, textvariable=shift_type_var, values=["شفت النهار", "شفت الليل"], state="readonly")
        shift_type_combo.grid(row=1, column=1, sticky="ew", pady=5)

        def save_changes():
            new_revenue = float(revenue_entry.get())
            new_shift_type = shift_type_var.get()

            edit_date = datetime.strptime(date, "%Y-%m-%d").date()

            # Check if changing the shift type would result in a duplicate entry
            if new_shift_type != shift_type:
                existing_entry = next((entry for entry in self.daily_revenue_data 
                                       if entry[0] == edit_date and entry[3] == new_shift_type), None)
                if existing_entry:
                    messagebox.showerror("خطأ", "عفوا لا يمكنك تغيير نوع الشفت لأنه يوجد إيراد مسجل لهذا الشفت في نفس اليوم")
                    return

            for i, entry in enumerate(self.daily_revenue_data):
                if entry[0] == edit_date and entry[1] == time:
                    self.daily_revenue_data[i] = (entry[0], entry[1], new_revenue, new_shift_type)
                    break

            self.update_daily_revenue_table()
            self.save_data()
            dialog.destroy()

        save_button = ttk.Button(dialog, text="حفظ التغييرات", command=save_changes)
        save_button.grid(row=2, column=0, columnspan=2, pady=10)

    def delete_daily_revenue(self):
        selected_item = self.daily_revenue_table.selection()
        if not selected_item:
            messagebox.showwarning("تحذير", "الرجاء تحديد عنصر للحذف")
            return

        if messagebox.askyesno("تأكيد الحذف", "هل أنت متأكد من رغبتك في حذف هذا العنصر؟"):
            item = self.daily_revenue_table.item(selected_item)
            date, time, _, _ = item['values']

            self.daily_revenue_data = [entry for entry in self.daily_revenue_data if not (entry[0] == datetime.strptime(date, "%Y-%m-%d").date() and entry[1] == time)]
            self.update_daily_revenue_table()
            self.save_data()

    def edit_supplier_cost(self):
        selected_item = self.supplier_costs_table.selection()
        if not selected_item:
            messagebox.showwarning("تحذير", "الرجاء تحديد عنصر للتعديل")
            return

        item = self.supplier_costs_table.item(selected_item)
        date, time, supplier, goods_type, notes, cost, payment_type = item['values']

        # Create a dialog for editing
        dialog = tk.Toplevel(self.master)
        dialog.title("تعديل تكلفة المورد")

        ttk.Label(dialog, text="اسم المورد:").grid(row=0, column=0, sticky="e", pady=5)
        supplier_entry = ttk.Entry(dialog)
        supplier_entry.insert(0, supplier)
        supplier_entry.grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(dialog, text="نوع البضاعة:").grid(row=1, column=0, sticky="e", pady=5)
        goods_type_entry = ttk.Entry(dialog)
        goods_type_entry.insert(0, goods_type)
        goods_type_entry.grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(dialog, text="ملاحظات:").grid(row=2, column=0, sticky="e", pady=5)
        notes_entry = ttk.Entry(dialog)
        notes_entry.insert(0, notes)
        notes_entry.grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Label(dialog, text="التكلفة:").grid(row=3, column=0, sticky="e", pady=5)
        cost_entry = ttk.Entry(dialog)
        cost_entry.insert(0, cost)
        cost_entry.grid(row=3, column=1, sticky="ew", pady=5)

        ttk.Label(dialog, text="نوع الدفع:").grid(row=4, column=0, sticky="e", pady=5)
        payment_type_var = tk.StringVar(value=payment_type)
        payment_type_combo = ttk.Combobox(dialog, textvariable=payment_type_var, values=["كاش", "آجل"], state="readonly")
        payment_type_combo.grid(row=4, column=1, sticky="ew", pady=5)

        def save_changes():
            new_supplier = supplier_entry.get()
            new_goods_type = goods_type_entry.get()
            new_notes = notes_entry.get()
            new_cost = float(cost_entry.get())
            new_payment_type = payment_type_var.get()

            for i, entry in enumerate(self.supplier_costs_data):
                if entry[0] == datetime.strptime(date, "%Y-%m-%d").date() and entry[1] == time:
                    self.supplier_costs_data[i] = (entry[0], entry[1], new_supplier, new_goods_type, new_notes, new_cost, new_payment_type)
                    break

            self.update_supplier_costs_table()
            self.save_data()
            dialog.destroy()

        save_button = ttk.Button(dialog, text="حفظ التغييرات", command=save_changes)
        save_button.grid(row=5, column=0, columnspan=2, pady=10)

    def delete_supplier_cost(self):
        selected_item = self.supplier_costs_table.selection()
        if not selected_item:
            messagebox.showwarning("تحذير", "الرجاء تحديد عنصر للحذف")
            return

        if messagebox.askyesno("تأكيد الحذف", "هل أنت متأكد من رغبتك في حذف هذا العنصر؟"):
            item = self.supplier_costs_table.item(selected_item)
            date, time, _, _, _, _, _ = item['values']

            self.supplier_costs_data = [entry for entry in self.supplier_costs_data if not (entry[0] == datetime.strptime(date, "%Y-%m-%d").date() and entry[1] == time)]
            self.update_supplier_costs_table()
            self.save_data()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernRevenueManagementUI(root)
    root.mainloop()