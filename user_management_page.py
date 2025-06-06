import tkinter as tk
from tkinter import ttk, messagebox
from data_connection import connect_to_replica  # Ensure this connects to your MySQL/DB

class UserManagementPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_rows = set()

        ttk.Label(self, text="User Management", font=("Arial", 18)).pack(pady=10)

        
        filter_frame = ttk.LabelFrame(self, text="Search Filters")
        filter_frame.pack(pady=5, fill="x", padx=10)

        ttk.Label(filter_frame, text="User ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.userid_entry = ttk.Entry(filter_frame, width=10)
        self.userid_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(filter_frame, text="Full Name:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.username_entry = ttk.Entry(filter_frame, width=20)
        self.username_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(filter_frame, text="Search", command=self.load_users).grid(row=0, column=4, padx=10)

        
        columns = ["Select", "User ID", "Full Name", "Phone", "City ID"]
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100 if col != "Full Name" else 180)

        self.tree.bind("<Button-1>", self.handle_click)

        
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Edit User", command=self.edit_user).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Delete User", command=self.delete_user).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Back to Admin", command=lambda: controller.show_frame("AdminPage")).grid(row=0, column=2, padx=5)

        self.load_users()

    def load_users(self):
        self.tree.delete(*self.tree.get_children())
        self.selected_rows.clear()

        uid_filter = self.userid_entry.get().strip()
        name_filter = self.username_entry.get().strip().lower()

        sql = """
            SELECT user_id, full_name, phone, city_id
            FROM main_db.user_profiles
            WHERE 1=1
        """
        params = []

        if uid_filter:
            sql += " AND user_id = %s"
            params.append(uid_filter)

        if name_filter:
            sql += " AND LOWER(full_name) LIKE %s"
            params.append(f"%{name_filter}%")

        try:
            conn = connect_to_replica()
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            results = cursor.fetchall()

            for row in results:
                tree_row = ("☐",) + row
                self.tree.insert("", "end", values=tree_row)

            cursor.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def handle_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.tree.identify_column(event.x)
        if column != "#1":  
            return

        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return

        current = self.tree.set(row_id, "Select")
        new = "✔" if current == "☐" else "☐"
        self.tree.set(row_id, "Select", new)

        if new == "✔":
            self.selected_rows.add(row_id)
        else:
            self.selected_rows.discard(row_id)

    def edit_user(self):
        if not self.selected_rows:
            messagebox.showwarning("No selection", "Please select a user to edit.")
            return

        row_id = list(self.selected_rows)[0]
        values = self.tree.item(row_id, "values")
        messagebox.showinfo("Edit User", f"Editing user: {values[2]} (functionality not implemented)")

    def delete_user(self):
        if not self.selected_rows:
            messagebox.showwarning("No selection", "Please select a user to delete.")
            return

        for row_id in list(self.selected_rows):
            values = self.tree.item(row_id, "values")
            username = values[2]
            confirm = messagebox.askyesno("Confirm Delete", f"Delete user '{username}'?")
            if confirm:
                self.tree.delete(row_id)
                self.selected_rows.discard(row_id)
                messagebox.showinfo("Deleted", f"User '{username}' deleted from view (not DB).")
