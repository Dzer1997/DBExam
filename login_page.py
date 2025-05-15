import tkinter as tk
from tkinter import ttk, messagebox
from data_connextion import connect_to_database  # Ensure this connects properly

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
        email = self.email_entry.get()
        password = self.password_entry.get()

        try:
            conn = connect_to_database()
            cursor = conn.cursor()

            cursor.callproc("GetUserRole", [email, password])

            for result in cursor.stored_results():
                data = result.fetchone()

            if data:
                user_role = data[0]

                if user_role == "admin":
                    messagebox.showinfo("Success", "Logged in as admin.")
                   
                elif user_role == "traveler":
                    messagebox.showinfo("Success", "Logged in as traveler.")
                    self.controller.show_frame("TravelerPage")

                else:
                    messagebox.showwarning("Login", "Unknown user role.")
            else:
                messagebox.showerror("Login Failed", "Incorrect email or password.")

            cursor.close()
            conn.close()

        except Exception as e:
            print("Database error:", e)
            messagebox.showerror("Error", "An error occurred while logging in.")
    def reset_fields(self):
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)