import tkinter as tk
from tkinter import ttk, messagebox
from data_connextion import connect_to_database
from tkcalendar import Calendar


class PlaneTicketPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Search for Plane Tickets", font=("Arial", 18)).pack(pady=10)

        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="From (Airport Code):").grid(row=0, column=0, padx=5, pady=5)
        self.from_combobox = ttk.Combobox(form_frame, width=30)
        self.from_combobox.grid(row=0, column=1, padx=5)

        ttk.Label(form_frame, text="To (Airport Code):").grid(row=0, column=2, padx=5, pady=5)
        self.to_combobox = ttk.Combobox(form_frame, width=30)
        self.to_combobox.grid(row=0, column=3, padx=5)

        ttk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        self.date_entry = ttk.Entry(form_frame)
        self.date_entry.grid(row=1, column=1, padx=5)

        self.date_calendar = Calendar(form_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.date_calendar.grid(row=2, column=1, padx=5, pady=5)


        ttk.Label(form_frame, text="Class:").grid(row=1, column=2, padx=5, pady=5)
        self.class_combobox = ttk.Combobox(form_frame, values=["Economy", "Business", "First Class"])
        self.class_combobox.grid(row=1, column=3, padx=5)
        self.class_combobox.set("Economy")

    
        ttk.Button(self, text="Search", command=self.search_flights).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("flight_id", "airline", "departure_time", "arrival_time", "class_type", "price"), show="headings")
        self.tree.pack(pady=10, fill="both", expand=True)

        
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col.capitalize())

        ttk.Button(self, text="Back", command=lambda: controller.show_frame("TravelerPage")).pack(pady=10)

        self.load_airports()

    def load_airports(self):
        """ Load all airport codes into the comboboxes """
        try:
            conn = connect_to_database()
            cursor = conn.cursor()

    
            cursor.execute("SELECT airport_code FROM Airports")
            airports = cursor.fetchall()

            airport_codes = [airport[0] for airport in airports]

            self.from_combobox['values'] = airport_codes
            self.to_combobox['values'] = airport_codes

            cursor.close()
            conn.close()

        except Exception as e:
            print("Database error:", e)
            messagebox.showerror("Error", "Failed to load airport codes.")

    def search_flights(self):
        origin = self.from_combobox.get().upper()  
        destination = self.to_combobox.get().upper()  
        date = self.date_entry.get()
        departure_date = self.date_calendar.get_date()
        flight_class = self.class_combobox.get()

        try:
            conn = connect_to_database()
            cursor = conn.cursor()

        
            query = """
                SELECT f.flight_id, a.airline_name, f.departure_time, f.arrival_time, fc.class_type, fc.price
                FROM Flights f
                JOIN flights_classes fc ON f.flight_id = fc.flight_id
                JOIN FlightRoute fr ON f.flight_id = fr.flight_id
                JOIN Airports start_airport ON f.start_airport_code = start_airport.airport_code
                JOIN Airports end_airport ON f.end_airport_code = end_airport.airport_code
                JOIN airlines a ON f.airline_id = a.airline_id
                WHERE f.start_airport_code = %s 
                AND f.end_airport_code = %s
                AND f.departure_time >= %s
                AND fc.class_type = %s
                ORDER BY f.departure_time
            """

        
            cursor.execute(query, (origin, destination, date,departure_date, flight_class))
            results = cursor.fetchall()

            
            for row in self.tree.get_children():
                self.tree.delete(row)

            if results:
                for row in results:
                    self.tree.insert("", "end", values=row)
            else:
                messagebox.showinfo("No Results", "No matching flights found.")

            cursor.close()
            conn.close()
        except Exception as e:
            print("Database error:", e)
            messagebox.showerror("Error", "Failed to search for flights.")
