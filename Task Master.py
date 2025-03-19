import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import uuid

class TaskManagerGUI:
    def __init__(self, root, filename="tasks.json"):
        self.root = root
        self.root.title("Task Manager")
        self.filename = filename
        self.tasks = self.load_tasks()

        # UI Layout
        self.create_widgets()
        self.populate_tasks()

    def load_tasks(self):
        try:
            with open(self.filename, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_tasks(self):
        with open(self.filename, "w") as file:
            json.dump(self.tasks, file, indent=4)

    def create_widgets(self):
        # Task List (Treeview)
        columns = ("ID", "Title", "Category", "Deadline", "Priority", "Status")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_tasks(c))
            self.tree.column(col, width=120)
        self.tree.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        # Input Fields
        ttk.Label(self.root, text="Title:").grid(row=1, column=0)
        self.title_entry = ttk.Entry(self.root)
        self.title_entry.grid(row=1, column=1)

        ttk.Label(self.root, text="Category:").grid(row=2, column=0)
        self.category_entry = ttk.Entry(self.root)
        self.category_entry.grid(row=2, column=1)

        ttk.Label(self.root, text="Deadline (YYYY-MM-DD):").grid(row=3, column=0)
        self.deadline_entry = ttk.Entry(self.root)
        self.deadline_entry.grid(row=3, column=1)

        ttk.Label(self.root, text="Priority:").grid(row=4, column=0)
        self.priority_combo = ttk.Combobox(self.root, values=["Low", "Medium", "High"])
        self.priority_combo.grid(row=4, column=1)

        # Buttons
        ttk.Button(self.root, text="Add Task", command=self.add_task).grid(row=5, column=0, padx=5, pady=5)
        ttk.Button(self.root, text="Edit Task", command=self.edit_task).grid(row=5, column=1, padx=5, pady=5)
        ttk.Button(self.root, text="Delete Task", command=self.delete_task).grid(row=5, column=2, padx=5, pady=5)
        ttk.Button(self.root, text="Complete Task", command=self.complete_task).grid(row=5, column=3, padx=5, pady=5)

    def populate_tasks(self):
        """ Refreshes task list in the GUI """
        self.tree.delete(*self.tree.get_children())  # Clear previous entries
        for task in self.tasks:
            self.tree.insert("", "end", values=(task["id"], task["title"], task["category"], task["deadline"], task["priority"], "Completed" if task["completed"] else "Pending"))

    def add_task(self):
        """ Adds a new task """
        title = self.title_entry.get()
        category = self.category_entry.get()
        deadline = self.deadline_entry.get()
        priority = self.priority_combo.get()

        if not title or not category or not deadline or not priority:
            messagebox.showerror("Error", "All fields must be filled!")
            return

        try:
            datetime.strptime(deadline, "%Y-%m-%d")  # Validate date format
        except ValueError:
            messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD.")
            return

        task = {
            "id": str(uuid.uuid4()),
            "title": title,
            "category": category,
            "deadline": deadline,
            "priority": priority,
            "completed": False
        }
        self.tasks.append(task)
        self.save_tasks()
        self.populate_tasks()
        messagebox.showinfo("Success", "Task added successfully!")

    def edit_task(self):
        """ Edits a selected task """
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No task selected!")
            return

        item = self.tree.item(selected)
        task_id = item["values"][0]

        for task in self.tasks:
            if task["id"] == task_id:
                task["title"] = self.title_entry.get() or task["title"]
                task["category"] = self.category_entry.get() or task["category"]
                task["deadline"] = self.deadline_entry.get() or task["deadline"]
                task["priority"] = self.priority_combo.get() or task["priority"]
                self.save_tasks()
                self.populate_tasks()
                messagebox.showinfo("Success", "Task updated successfully!")
                return

    def delete_task(self):
        """ Deletes a selected task """
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No task selected!")
            return

        item = self.tree.item(selected)
        task_id = item["values"][0]

        self.tasks = [task for task in self.tasks if task["id"] != task_id]
        self.save_tasks()
        self.populate_tasks()
        messagebox.showinfo("Success", "Task deleted successfully!")

    def complete_task(self):
        """ Marks a task as completed """
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No task selected!")
            return

        item = self.tree.item(selected)
        task_id = item["values"][0]

        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                self.save_tasks()
                self.populate_tasks()
                messagebox.showinfo("Success", "Task marked as completed!")
                return

    def sort_tasks(self, column):
        """ Sorts tasks based on the selected column """
        if column == "Priority":
            priority_order = {"High": 1, "Medium": 2, "Low": 3}
            self.tasks.sort(key=lambda task: priority_order[task["priority"]])
        elif column == "Deadline":
            self.tasks.sort(key=lambda task: datetime.strptime(task["deadline"], "%Y-%m-%d"))
        elif column == "Title":
            self.tasks.sort(key=lambda task: task["title"].lower())

        self.populate_tasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerGUI(root)
    root.mainloop()
