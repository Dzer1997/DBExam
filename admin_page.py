import tkinter as tk
from tkinter import ttk

class AdminPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ttk.Label(self, text="Admin Dashboard", font=("Arial", 20)).pack(pady=20)
        ttk.Label(self, text="Manage users, listings, and bookings.").pack(pady=10)

        ttk.Button(self, text="Edit/Delete Users", command=lambda: controller.show_frame("UserManagementPage")).pack(pady=10)

        ttk.Button(self, text="Add New Flight", command=lambda: controller.show_frame("AddFlightPage")).pack(pady=10)
        ttk.Button(self, text="Edit/Delete Flights", command=lambda: controller.show_frame("ManageFlightsPage")).pack(pady=10)

        
        ttk.Button(self, text="Add New Airbnb", command=lambda: controller.show_frame("AddAirbnbPage")).pack(pady=10)
        ttk.Button(self, text="Edit/Delete Airbnb", command=lambda: controller.show_frame("ManageAirbnbPage")).pack(pady=10)

        ttk.Button(self, text="View Packages", command=lambda: controller.show_frame("PackagesPage")).pack(pady=10)
        ttk.Button(self, text="My Booking", command=lambda: controller.show_frame("BookingPage")).pack(pady=10)
        ttk.Button(self, text="Back to Home", command=lambda: controller.show_frame("HomePage")).pack(pady=10)

