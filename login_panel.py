import tkinter as tk
from tkinter import messagebox, font
import hashlib

class ModernLoginPanel:
    def __init__(self, master, on_login_success):
        self.master = master
        self.master.title("Restaurant POS Login")
        self.master.geometry("1366x768")
        self.master.resizable(False, False)
        self.on_login_success = on_login_success

        # Load Tajawal font
        self.load_tajawal_font()

        self.create_widgets()

    def load_tajawal_font(self):
        # Load Tajawal font
        self.tajawal_bold = font.Font(family="Tajawal", size=60, weight="bold")  # Reduced from 72 to 60
        self.tajawal_regular = font.Font(family="Tajawal", size=16)

    def create_widgets(self):
        # Set background color
        self.master.configure(bg="#f4f7fa")

        # Main frame
        main_frame = tk.Frame(self.master, bg="#ffffff", width=1000, height=600)
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Add subtle shadow
        main_frame.config(highlightbackground="#e0e0e0", highlightthickness=1)

        # Left panel (logo and tagline)
        left_panel = tk.Frame(main_frame, bg="#ffffff", width=400, height=600)
        left_panel.pack(side="left", fill="both")

        # Logo
        logo_label = tk.Label(left_panel, text="مطعم غنو", font=self.tajawal_bold, bg="#ffffff", fg="#3498db")
        logo_label.place(relx=0.5, rely=0.4, anchor="center")

        # Tagline
        tagline_label = tk.Label(left_panel, text="اجمل واشهي الاكلات", font=self.tajawal_regular, bg="#ffffff", fg="#7f8c8d")
        tagline_label.place(relx=0.5, rely=0.5, anchor="center")

        # Right panel (login form)
        right_panel = tk.Frame(main_frame, bg="#ffffff", width=600, height=600)
        right_panel.pack(side="right", fill="both", expand=True)

        # Title
        tk.Label(right_panel, text="Welcome Back", font=("Helvetica", 32, "bold"), bg="#ffffff", fg="#2c3e50").place(x=50, y=100)
        tk.Label(right_panel, text="Please sign in to your account", font=("Helvetica", 14), bg="#ffffff", fg="#7f8c8d").place(x=50, y=150)

        # Username
        username_frame = tk.Frame(right_panel, bg="#ffffff", width=450, height=60)
        username_frame.place(x=50, y=220)
        self.username_entry = tk.Entry(username_frame, font=("Helvetica", 14), width=30, bd=0, bg="#ffffff")
        self.username_entry.place(x=0, y=30)
        self.username_entry.insert(0, "Username")
        self.username_entry.bind("<FocusIn>", lambda e: self.on_entry_click(e, "Username"))
        self.username_entry.bind("<FocusOut>", lambda e: self.on_focus_out(e, "Username"))
        tk.Frame(username_frame, bg="#3498db", width=450, height=2).place(x=0, y=55)

        # Password
        password_frame = tk.Frame(right_panel, bg="#ffffff", width=450, height=60)
        password_frame.place(x=50, y=300)
        self.password_entry = tk.Entry(password_frame, font=("Helvetica", 14), width=30, bd=0, bg="#ffffff")
        self.password_entry.place(x=0, y=30)
        self.password_entry.insert(0, "Password")
        self.password_entry.bind("<FocusIn>", lambda e: self.on_entry_click(e, "Password"))
        self.password_entry.bind("<FocusOut>", lambda e: self.on_focus_out(e, "Password"))
        tk.Frame(password_frame, bg="#3498db", width=450, height=2).place(x=0, y=55)

        # Login Button
        login_btn = tk.Button(right_panel, text="SIGN IN", command=self.login, font=("Helvetica", 14, "bold"),
                              bg="#3498db", fg="white", width=20, height=2, bd=0, cursor="hand2")
        login_btn.place(x=50, y=400)
        login_btn.bind("<Enter>", lambda e: login_btn.config(bg="#2980b9"))
        login_btn.bind("<Leave>", lambda e: login_btn.config(bg="#3498db"))

        # Forgot Password
        forgot_password = tk.Label(right_panel, text="Forgot Password?", font=("Helvetica", 12), bg="#ffffff", fg="#3498db", cursor="hand2")
        forgot_password.place(x=50, y=470)
        forgot_password.bind("<Button-1>", lambda e: messagebox.showinfo("Forgot Password", "Please contact your system administrator."))

        # Credits
        credits_label = tk.Label(right_panel, text="Developed by Dr Ahmed Elhoseny", 
                                 font=("Helvetica", 10), bg="#ffffff", fg="#7f8c8d")
        credits_label.place(relx=0.5, rely=0.95, anchor="center")

    def on_entry_click(self, event, default_text):
        """Function to handle entry click event"""
        widget = event.widget
        if widget.get() == default_text:
            widget.delete(0, "end")
            widget.config(fg="#2c3e50")
            if default_text == "Password":
                widget.config(show="•")

    def on_focus_out(self, event, default_text):
        """Function to handle focus out event"""
        widget = event.widget
        if widget.get() == '':
            widget.insert(0, default_text)
            widget.config(fg="#7f8c8d")
            if default_text == "Password":
                widget.config(show="")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "Username" or password == "Password":
            messagebox.showerror("Login Failed", "Please enter both username and password")
            return

        role = self.authenticate(username, password)
        if role:
            self.master.destroy()  # Close the login window
            self.on_login_success(username, role)  # This line is correct now
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def authenticate(self, username, password):
        # Dictionary of users with their hashed passwords and roles
        users = {
            "admin": {"password": self.hash_password("1"), "role": "admin"},
            "1": {"password": self.hash_password("1"), "role": "cashier"},
            "2": {"password": self.hash_password("2"), "role": "cashier"},
            # Add more users here as needed
        }

        if username in users and self.hash_password(password) == users[username]["password"]:
            return users[username]["role"]
        return None

    def hash_password(self, password):
        # Use SHA-256 for hashing
        salt = "mysalt"  # In a real application, use a unique salt for each user
        return hashlib.sha256((password + salt).encode()).hexdigest()

def start_login(on_login_success):
    root = tk.Tk()
    ModernLoginPanel(root, on_login_success)
    root.mainloop()

if __name__ == "__main__":
    # This is just for testing the login panel independently
    def on_successful_login(username, role):  # Update this to accept both username and role
        print(f"Login successful for user: {username} with role: {role}")

    start_login(on_successful_login)