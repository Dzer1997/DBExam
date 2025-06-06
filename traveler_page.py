import tkinter as tk
from tkinter import ttk

class TravelerPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        ttk.Label(self, text="Traveler Dashboard", font=("Arial", 20)).pack(pady=20)
        ttk.Label(self, text="Here you can book tickets or find Airbnb.").pack(pady=10)
        ttk.Button(self, text="Buy Plane Ticket", command=lambda: controller.show_frame("PlaneTicketPage")).pack(pady=10)
        ttk.Button(self, text="Book Airbnb", command=lambda: controller.show_frame("AirbnbPage")).pack(pady=10)
        ttk.Button(self, text="View Packages", command=lambda: controller.show_frame("PackagesPage")).pack(pady=10)
        ttk.Button(self, text="My Booking", command=lambda: controller.show_frame("BookingPage")).pack(pady=10)
        ttk.Button(self, text="Back to Home", command=lambda: controller.show_frame("HomePage")).pack(pady=10)
