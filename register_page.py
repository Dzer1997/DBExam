import tkinter as tk
from tkinter import ttk, messagebox
from data_connection import  execute_write, connect_to_replica,call_procedure
import mysql.connector
from mysql.connector import Error

class RegisterPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

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
        """Load city names from the DB into the combobox."""
        try:
            conn =  connect_to_replica()
            cursor = conn.cursor()
            cursor.execute("SELECT city_name FROM cities")
            cities = [row[0] for row in cursor.fetchall()]
            if cities:
                self.city_combobox['values'] = cities
                self.city_combobox.current(0)
            else:
                self.city_combobox['values'] = []
            cursor.close()
            conn.close()
        except Exception as e:
            print("Failed to load cities:", e)
            messagebox.showerror("Error", "Could not load cities from the database.")

    def register_user(self):
        """Register the user using the stored procedure."""
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_combobox.get()
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        city_name = self.city_combobox.get()

        if not all([email, password, role, name, phone, city_name]):
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        try:
        
            call_procedure("register_user", [email, password, role, name, phone, city_name])

            messagebox.showinfo("Success", "User registered successfully.")

            
            self.email_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.name_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)
            self.role_combobox.current(0)
            self.city_combobox.current(0)

        except mysql.connector.Error as e:
            print("MySQL Error:", e)
            messagebox.showerror("Database Error", f"MySQL Error:\n{e}")
        except Exception as e:
            print("General Error:", e)
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")
