import tkinter as tk
from tkinter import ttk
from register_page import RegisterPage
from login_page import LoginPage

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Travel Booking System")
        self.geometry("800x600")

        self.frames = {} 

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        for F in (HomePage, RegisterPage, LoginPage):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

class HomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)


        label = ttk.Label(self, text="Welcome to Travel Booking", font=("Arial", 20), style="Custom.TLabel")
        label.pack(pady=20)

        ttk.Button(self, text="Login", command=lambda: controller.show_frame("LoginPage")).pack(pady=10)
        ttk.Button(self, text="Register", command=lambda: controller.show_frame("RegisterPage")).pack(pady=10)

if __name__ == "__main__":
    app = App()
    app.mainloop()
