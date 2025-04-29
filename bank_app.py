import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime
from decimal import Decimal

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="mouli",
    password="Pass@06sql",
    database="bank_management"
)
cursor = db.cursor()

def add_transaction(username, t_type, amount):
    cursor.execute("INSERT INTO transactions (account_name, transaction_type, amount) VALUES (%s, %s, %s)",
                   (username, t_type, amount))
    db.commit()

# Main Application
class BankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bank Account Management")
        self.root.geometry("600x500")
        self.root.config(bg="#f0f4f7")
        self.username = None
        self.build_login()

    def build_login(self):
        self.clear_window()

        tk.Label(self.root, text="Login / Register", font=("Arial", 20, 'bold'), bg="#f0f4f7").pack(pady=20)
        tk.Label(self.root, text="Username:", bg="#f0f4f7").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Label(self.root, text="Password:", bg="#f0f4f7").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        tk.Button(self.root, text="Login", bg="#4CAF50", fg="white", command=self.login).pack(pady=10)
        tk.Button(self.root, text="Register", bg="#2196F3", fg="white", command=self.register).pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        result = cursor.fetchone()
        if result:
            self.username = username
            self.build_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            db.commit()
            messagebox.showinfo("Success", "User registered successfully!")
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Username already exists")

    def build_dashboard(self):
        self.clear_window()
        tk.Label(self.root, text=f"Welcome {self.username}", font=("Arial", 16, 'bold'), bg="#f0f4f7").pack(pady=10)

        # Balance info
        cursor.execute("SELECT balance FROM users WHERE username = %s", (self.username,))
        balance = cursor.fetchone()[0]
        self.balance_label = tk.Label(self.root, text=f"Balance: ₹{balance:.2f}", font=("Arial", 14), bg="#f0f4f7")
        self.balance_label.pack(pady=5)

        # Transaction Buttons
        tk.Button(self.root, text="Deposit", bg="#4CAF50", fg="white", width=20, command=self.deposit_screen).pack(pady=5)
        tk.Button(self.root, text="Withdraw", bg="#f44336", fg="white", width=20, command=self.withdraw_screen).pack(pady=5)
        tk.Button(self.root, text="View Transactions", bg="#2196F3", fg="white", width=20, command=self.show_transactions).pack(pady=5)
        tk.Button(self.root, text="Logout", bg="grey", fg="white", command=self.build_login).pack(pady=10)

    def deposit_screen(self):
        self.transaction_window("Deposit")

    def withdraw_screen(self):
        self.transaction_window("Withdraw")

    def transaction_window(self, t_type):
        win = tk.Toplevel(self.root)
        win.title(t_type)
        win.geometry("300x200")
        win.config(bg="#f0f4f7")

        tk.Label(win, text=f"Enter amount to {t_type}", bg="#f0f4f7").pack(pady=10)
        amount_entry = tk.Entry(win)
        amount_entry.pack()

        def perform():
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Enter a valid amount")
                return

            cursor.execute("SELECT balance FROM users WHERE username = %s", (self.username,))
            current_balance = cursor.fetchone()[0]

            if t_type == "Withdraw" and amount > current_balance:
                messagebox.showerror("Error", "Insufficient balance")
                return

            amount = Decimal(amount)
            new_balance = current_balance + amount if t_type == "Deposit" else current_balance - amount
            cursor.execute("UPDATE users SET balance = %s WHERE username = %s", (new_balance, self.username))
            db.commit()

            add_transaction(self.username, t_type, amount)
            self.balance_label.config(text=f"Balance: ₹{new_balance:.2f}")
            messagebox.showinfo("Success", f"{t_type} successful")
            win.destroy()

        tk.Button(win, text=t_type, bg="#4CAF50" if t_type == "Deposit" else "#f44336", fg="white", command=perform).pack(pady=10)

    def show_transactions(self):
        win = tk.Toplevel(self.root)
        win.title("Transaction History")
        win.geometry("500x300")

        tree = ttk.Treeview(win, columns=("ID", "Type", "Amount", "Date"), show='headings')
        tree.heading("ID", text="ID")
        tree.heading("Type", text="Type")
        tree.heading("Amount", text="Amount")
        tree.heading("Date", text="Date")

        tree.pack(fill=tk.BOTH, expand=True)

        cursor.execute("SELECT id, transaction_type, amount, transaction_date FROM transactions WHERE account_name = %s ORDER BY transaction_date DESC", (self.username,))
        for row in cursor.fetchall():
           tree.insert("", "end", values=(row[0], row[1], row[2], row[3]))


    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = BankApp(root)
    root.mainloop()
