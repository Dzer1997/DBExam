import tkinter as tk
from tkinter import ttk
import json
from data_connection import redis_client 
from my_booking_page import BookingPage
from register_page import RegisterPage
from login_page import LoginPage
from traveler_page import TravelerPage
from airbnb_page import AirbnbPage
from packages_page import PackagesPage
from plane_ticket_page import PlaneTicketPage
from FlightDetailsPage import FlightDetailsPage
from AirbnbDetailsPage import AirbnbDetailsPage
from admin_page import AdminPage
from user_management_page import UserManagementPage

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Travel Booking System")
        self.geometry("800x600")

        self.frames = {}
        self.current_user_id = None  

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        # Initialize all pages
        for F in (
            HomePage, RegisterPage, LoginPage,
            TravelerPage, PlaneTicketPage,
            AirbnbPage, PackagesPage, FlightDetailsPage, AirbnbDetailsPage, BookingPage,AdminPage,UserManagementPage
        ):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")

    def show_frame(self, page_name, **kwargs):
        frame = self.frames[page_name]

        if hasattr(frame, "reset_fields"):
            frame.reset_fields()

        if "data" in kwargs and hasattr(frame, "load_data"):
            frame.load_data(kwargs["data"])

        elif page_name == "AirbnbDetailsPage" and hasattr(frame, "load_data"):
            try:
                user_id = self.current_user_id
                if not user_id:
                    raise ValueError("User not logged in")

                redis_key = f"user:{user_id}:selected_airbnbs"
                cached_data = redis_client.get(redis_key)

                if cached_data:
                    data = json.loads(cached_data)
                    print("Loaded data from Redis:", data)
                    frame.load_data(data)
                else:
                    print("No data found in Redis or key expired.")
                    frame.load_data([])

            except Exception as e:
                print("Error fetching data from Redis:", e)
                frame.load_data([])

        frame.tkraise()

class HomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        label = ttk.Label(self, text="Welcome to Travel Booking", font=("Arial", 20))
        label.pack(pady=20)

        ttk.Button(self, text="Login", command=lambda: controller.show_frame("LoginPage")).pack(pady=10)
        ttk.Button(self, text="Register", command=lambda: controller.show_frame("RegisterPage")).pack(pady=10)

if __name__ == "__main__":
    app = App()
    app.mainloop()
