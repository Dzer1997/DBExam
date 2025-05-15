import tkinter as tk
from tkinter import ttk
from register_page import RegisterPage
from login_page import LoginPage
from traveler_page import TravelerPage
from airbnb_page import AirbnbPage
from packages_page import PackagesPage
from plane_ticket_page import PlaneTicketPage


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Travel Booking System")
        self.geometry("800x600")

        self.frames = {}

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        for F in (
            HomePage, RegisterPage, LoginPage,
            TravelerPage, PlaneTicketPage, AirbnbPage, PackagesPage
        ):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if hasattr(frame, "reset_fields"):
            frame.reset_fields()
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
