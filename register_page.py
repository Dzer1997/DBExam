import tkinter as tk
from tkinter import ttk, messagebox
from data_connextion import connect_to_database
from mysql.connector import Error
import mysql.connector

class RegisterPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ttk.Label(self, text="Register", font=("Arial", 20)).pack(pady=20)

        ttk.Label(self, text="Email", font=("Arial", 16)).pack()
        self.email_entry = ttk.Entry(self, width=30)
        self.email_entry.pack()

        ttk.Label(self, text="Password", font=("Arial", 16)).pack()
        self.password_entry = ttk.Entry(self, show="*", width=30)
        self.password_entry.pack()

        ttk.Label(self, text="Role", font=("Arial", 16)).pack()
        self.role_combobox = ttk.Combobox(self, values=["admin", "traveler"], state="readonly", width=28)
        self.role_combobox.current(0)
        self.role_combobox.pack()

        ttk.Label(self, text="Full Name", font=("Arial", 16)).pack()
        self.name_entry = ttk.Entry(self, width=30)
        self.name_entry.pack()

        ttk.Label(self, text="Phone", font=("Arial", 16)).pack()
        self.phone_entry = ttk.Entry(self, width=30)
        self.phone_entry.pack()

        ttk.Label(self, text="Select City", font=("Arial", 14)).pack(pady=10)
        self.city_combobox = ttk.Combobox(self, width=30)
        self.city_combobox.pack()

        self.load_cities()

        ttk.Button(self, text="Register", command=self.register_user).pack(pady=10)
        ttk.Button(self, text="Back to Home", command=lambda: controller.show_frame("HomePage")).pack(pady=10)

    def load_cities(self):
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("SELECT city_name FROM cities")
            cities = [row[0] for row in cursor.fetchall()]
            self.city_combobox['values'] = cities
            cursor.close()
            conn.close()
        except Exception as e:
            print("Failed to load cities:", e)

    def register_user(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        role = self.role_combobox.get()
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        city = self.city_combobox.get()

        try:
            conn = connect_to_database()
            cursor = conn.cursor()

            cursor.execute("SELECT city_id FROM cities WHERE city_name = %s", (city,))
            city_row = cursor.fetchone()
            if not city_row:
                messagebox.showerror("Error", "Selected city not found.")
                return
            city_id = city_row[0]

            cursor.callproc("register_user", [email, password, role, name, phone, city_id])
            conn.commit()
            messagebox.showinfo("Success", "User registered successfully.")

            cursor.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to register user:\n{e}")
