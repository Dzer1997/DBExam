import tkinter as tk
from tkinter import ttk

class AirbnbPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        ttk.Label(self, text="Book Airbnb", font=("Arial", 20)).pack(pady=20)

        # Placeholder UI
        ttk.Label(self, text="(Airbnb options go here)").pack(pady=10)

        ttk.Button(self, text="Back", command=lambda: controller.show_frame("TravelerPage")).pack(pady=20)
