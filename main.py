import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import matplotlib.pyplot as plt
from collections import defaultdict

class BudgetTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Maxwell's Budget Tracker")
        self.root.geometry("600x400")

        # Data Structures
        self.categories = ["Food", "Rent", "Entertainment", "Transport", "Others"]
        self.expenses = defaultdict(list)
        self.income = 0.0
        self.budget = {}

        # UI Components
        self.create_ui()

    def create_ui(self):
        # Income Section
        tk.Label(self.root, text="Income Section", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3, pady=5)
        tk.Label(self.root, text="Enter Income:").grid(row=1, column=0, padx=10, pady=5)
        self.income_entry = tk.Entry(self.root)
        self.income_entry.grid(row=1, column=1)
        tk.Button(self.root, text="Add Income", command=self.add_income).grid(row=1, column=2, padx=10, pady=5)

        # Budget Section
        tk.Label(self.root, text="Budget Section", font=("Arial", 12, "bold")).grid(row=2, column=0, columnspan=3, pady=5)
        tk.Button(self.root, text="Set Budget", command=self.set_budget).grid(row=3, column=0, padx=10, pady=5)

        # Expense Section
        tk.Label(self.root, text="Expense Section", font=("Arial", 12, "bold")).grid(row=4, column=0, columnspan=4, pady=5)
        tk.Label(self.root, text="Amount:").grid(row=5, column=0, padx=10, pady=5)
        self.expense_amount = tk.Entry(self.root)
        self.expense_amount.grid(row=5, column=1)
        
        tk.Label(self.root, text="Category:").grid(row=5, column=2)
        self.expense_category = ttk.Combobox(self.root, values=self.categories, state="readonly")
        self.expense_category.grid(row=5, column=3)
        
        tk.Button(self.root, text="Add Expense", command=self.add_expense).grid(row=5, column=4, padx=10)

        # Summary & Visualization Buttons
        tk.Button(self.root, text="Show Summary", command=self.show_summary).grid(row=6, column=0, padx=10, pady=10)
        tk.Button(self.root, text="Visualize Expenses", command=self.visualize_expenses).grid(row=6, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Visualize Income", command=self.visualize_income).grid(row=6, column=2, padx=10, pady=10)

    def add_income(self):
        try:
            amount = float(self.income_entry.get())
            if amount <= 0:
                messagebox.showerror("Error", "Income must be a positive number.")
                return
            self.income += amount
            messagebox.showinfo("Success", f"Income of ${amount:.2f} added!")
            self.income_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid income amount.")

    def set_budget(self):
        for category in self.categories:
            amount = simpledialog.askfloat("Budget Input", f"Enter budget for {category}")
            if amount is not None and amount >= 0:
                self.budget[category] = amount
            else:
                messagebox.showerror("Error", "Budget must be a non-negative number.")
        messagebox.showinfo("Success", "Budgets have been set!")

    def add_expense(self):
        try:
            amount = float(self.expense_amount.get())
            category = self.expense_category.get()

            if not category or category not in self.categories:
                messagebox.showerror("Error", "Please select a valid category.")
                return

            if amount <= 0:
                messagebox.showerror("Error", "Expense must be a positive number.")
                return

            self.expenses[category].append(amount)
            total_expense = sum(self.expenses[category])
            self.expense_amount.delete(0, tk.END)
            self.expense_category.set("")
            messagebox.showinfo("Success", f"Added expense of ${amount:.2f} in {category} category.")

            # Show a single warning if budget is exceeded
            if category in self.budget and total_expense > self.budget[category]:
                messagebox.showwarning("Budget Alert", f"You have exceeded your budget for {category}!")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid expense amount.")

    def show_summary(self):
        total_expenses = sum(sum(exp) for exp in self.expenses.values())
        savings = self.income - total_expenses
        summary = f"Total Income: ${self.income:.2f}\nTotal Expenses: ${total_expenses:.2f}\nSavings: ${savings:.2f}\n"

        for category, expenses in self.expenses.items():
            summary += f"{category}: ${sum(expenses):.2f} (Budget: ${self.budget.get(category, 'Not Set')})\n"

        messagebox.showinfo("Summary", summary)

    def visualize_expenses(self):
        categories = list(self.expenses.keys())
        expenses = [sum(self.expenses[cat]) for cat in categories]

        if expenses:
            plt.pie(expenses, labels=categories, autopct='%1.1f%%', startangle=90)
            plt.axis('equal')
            plt.title("Expense Breakdown")
            plt.show()
        else:
            messagebox.showinfo("No Data", "No expenses to visualize.")

    def visualize_income(self):
        total_expenses = sum(sum(exp) for exp in self.expenses.values())

        if self.income > 0:
            plt.bar(["Income", "Expenses"], [self.income, total_expenses], color=["green", "red"])
            plt.title("Income vs Expenses")
            plt.ylabel("Amount ($)")
            plt.show()
        else:
            messagebox.showinfo("No Data", "No income to visualize.")

# Main Application Loop
if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetTracker(root)
    root.mainloop()