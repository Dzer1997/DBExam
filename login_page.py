import tkinter as tk
from tkinter import ttk, messagebox
from data_connextion import connect_to_database
from mysql.connector import Error
import mysql.connector


class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller 

        ttk.Label(self, text="Email").pack()
        self.email_entry = ttk.Entry(self)
        self.email_entry.pack()

        ttk.Label(self, text="Password").pack()
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack()

        ttk.Button(self, text="Login", command=self.login).pack(pady=10)

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        try:
            conn = connect_to_database()
            cursor = conn.cursor()

            cursor.execute("SELECT role FROM users WHERE email = %s AND password = %s", (email, password))
            result = cursor.fetchone()

            if result:
                user_role = result[0]

                if user_role == "admin":
                    #self.controller.show_frame("AdminPage")
                    messagebox.showinfo("Success", f"Logged in as {user_role}.")
                else:
                    #self.controller.show_frame("HomePage")

                    messagebox.showinfo("Success", f"Logged in as {user_role}.")
            else:
                messagebox.showerror("Login Failed", "Incorrect email or password.")

            cursor.close()
            conn.close()

        except Exception as e:
            print("Database error:", e)
            messagebox.showerror("Error", "An error occurred while logging in.")
