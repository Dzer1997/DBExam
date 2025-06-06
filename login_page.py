import tkinter as tk
from tkinter import ttk, messagebox
from data_connection import connect_to_master, connect_to_replica


class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Email").pack(pady=5)
        self.email_entry = ttk.Entry(self)
        self.email_entry.pack(pady=5)

        ttk.Label(self, text="Password").pack(pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        ttk.Button(self, text="Login", command=self.login).pack(pady=10)
        ttk.Button(self, text="Back to Home", command=lambda: controller.show_frame("HomePage")).pack(pady=10)

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showwarning("Validation Error", "Email and password cannot be empty.")
            return

        try:
            conn = connect_to_replica()
            if not conn or not conn.is_connected():
                messagebox.showerror("Connection Error", "Unable to connect to the database.")
                return

            cursor = conn.cursor()
            cursor.callproc("GetUserRole", [email, password])

            data = None
            for result in cursor.stored_results():
                data = result.fetchone()

            if data:
                user_role, user_id = data  
                self.controller.current_user_id = user_id  

                if user_role == "admin":
                    messagebox.showinfo("Login Successful", "Welcome, Admin!")
                    self.controller.show_frame("AdminPage")  

                elif user_role == "traveler":
                    messagebox.showinfo("Login Successful", "Welcome, Traveler!")
                    self.controller.show_frame("TravelerPage")

                else:
                    messagebox.showwarning("Login Error", "Unknown user role.")
            else:
                messagebox.showerror("Login Failed", "Incorrect email or password.")

            cursor.close()
            conn.close()

        except Exception as e:
            print("Database error:", e)
            messagebox.showerror("Error", f"An error occurred: {e}")

    def reset_fields(self):
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
