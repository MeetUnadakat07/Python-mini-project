import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt


class Database:
    def __init__(self, db_name="expenses.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def add_expense(self, amount, category, date):
        query = "INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)"
        self.conn.execute(query, (amount, category, date))
        self.conn.commit()

    def delete_expense(self, row_id):
        query = "DELETE FROM expenses WHERE id = ?"
        self.conn.execute(query, (row_id,))
        self.conn.commit()

    def fetch_all(self):
        query = "SELECT * FROM expenses"
        cursor = self.conn.execute(query)
        return cursor.fetchall()

    def fetch_monthly_data(self):
        query = "SELECT category, SUM(amount) FROM expenses GROUP BY category"
        cursor = self.conn.execute(query)
        return cursor.fetchall()


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Expense Tracker")
        self.root.geometry("700x500")
        self.db = Database()

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Label(frame, text="Amount:").grid(row=0, column=0)
        self.amount_entry = tk.Entry(frame)
        self.amount_entry.grid(row=0, column=1)

        tk.Label(frame, text="Category:").grid(row=1, column=0)
        self.category_var = tk.StringVar()
        categories = ["Food", "Travel", "Entertainment", "Other"]
        self.category_menu = ttk.Combobox(frame, textvariable=self.category_var, values=categories)
        self.category_menu.grid(row=1, column=1)
        self.category_menu.set("Food")

        tk.Button(frame, text="Add Expense", command=self.add_expense).grid(row=2, column=0, columnspan=2, pady=10)

        columns = ("ID", "Amount", "Category", "Date")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.pack(fill=tk.BOTH, expand=True)

        tk.Button(self.root, text="Delete Selected", command=self.delete_selected).pack(pady=10)
        tk.Button(self.root, text="Show Pie Chart", command=self.show_pie_chart).pack(pady=5)

    def add_expense(self):
        try:
            amount = float(self.amount_entry.get())
            category = self.category_var.get()
            date = datetime.now().strftime("%Y-%m-%d")

            self.db.add_expense(amount, category, date)
            self.load_data()
            self.amount_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to delete.")
            return

        item = self.tree.item(selected[0])
        row_id = item["values"][0]
        self.db.delete_expense(row_id)
        self.load_data()

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for row in self.db.fetch_all():
            self.tree.insert("", tk.END, values=row)

    def show_pie_chart(self):
        data = self.db.fetch_monthly_data()
        if not data:
            messagebox.showinfo("Info", "No data to display.")
            return

        categories = [item[0] for item in data]
        amounts = [item[1] for item in data]

        plt.figure(figsize=(6, 6))
        plt.pie(amounts, labels=categories, autopct="%1.1f%%")
        plt.title("Monthly Spending Distribution")
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
