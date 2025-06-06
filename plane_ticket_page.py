import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from data_connection import connect_to_replica, redis_client
import json
from datetime import datetime

class PlaneTicketPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.full_results = []

        ttk.Label(self, text="Search for Plane Tickets", font=("Arial", 18)).pack(pady=10)

        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="From (City):").grid(row=0, column=0, padx=5, pady=5)
        self.from_combobox = ttk.Combobox(form_frame, width=30)
        self.from_combobox.grid(row=0, column=1, padx=5)

        ttk.Label(form_frame, text="To (City):").grid(row=0, column=2, padx=5, pady=5)
        self.to_combobox = ttk.Combobox(form_frame, width=30)
        self.to_combobox.grid(row=0, column=3, padx=5)

        ttk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        self.date_entry = ttk.Entry(form_frame)
        self.date_entry.grid(row=1, column=1, padx=5)

        ttk.Label(form_frame, text="Class:").grid(row=1, column=2, padx=5, pady=5)
        self.class_combobox = ttk.Combobox(form_frame, values=["Economy", "Business", "First Class"])
        self.class_combobox.grid(row=1, column=3, padx=5)
        self.class_combobox.set("Economy")

        ttk.Button(self, text="Search", command=self.search_flights).pack(pady=10)

        filter_frame = ttk.LabelFrame(self, text="Filters")
        filter_frame.pack(pady=5, fill="x", padx=10)

        ttk.Label(filter_frame, text="Airline:").grid(row=0, column=0, padx=5, pady=5)
        self.airline_filter = ttk.Combobox(filter_frame, values=["All"], width=15)
        self.airline_filter.set("All")
        self.airline_filter.grid(row=0, column=1)
        self.airline_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        ttk.Label(filter_frame, text="Min Price:").grid(row=0, column=2, padx=5, pady=5)
        self.min_price_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.min_price_var, width=10).grid(row=0, column=3)

        ttk.Label(filter_frame, text="Max Price:").grid(row=0, column=4, padx=5, pady=5)
        self.max_price_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.max_price_var, width=10).grid(row=0, column=5)

        ttk.Label(filter_frame, text="Departure Time:").grid(row=0, column=6, padx=5, pady=5)
        self.time_var = tk.StringVar()
        self.time_combobox = ttk.Combobox(filter_frame, textvariable=self.time_var, width=12,
                                          values=["", "Morning", "Afternoon", "Evening", "Night"])
        self.time_combobox.grid(row=0, column=7)

        ttk.Button(filter_frame, text="Apply Filters", command=self.apply_filters).grid(row=0, column=8, padx=10)

        self.tree = ttk.Treeview(
            self,
            columns=("Select", "flight_id", "airline", "departure_time", "arrival_time", "class_type", "price"),
            show="headings",
            selectmode="extended"
        )
        self.tree.pack(pady=10, fill="both", expand=True)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col.capitalize())
        self.tree.bind("<ButtonRelease-1>", self.toggle_selection)

        self.selected_flights = set()

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Show Selected", command=self.show_selected_flights).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Back", command=lambda: controller.show_frame("TravelerPage")).pack(side="left", padx=5)

        self.load_cities()

    def load_cities(self):
        try:
            conn = connect_to_replica()
            if not conn or not conn.is_connected():
                raise Exception("Failed to connect to replica.")
            cursor = conn.cursor()
            cursor.execute("SELECT city_name FROM cities")
            cities = [row[0] for row in cursor.fetchall()]
            self.from_combobox["values"] = cities
            self.to_combobox["values"] = cities
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load cities: {e}")

    def search_flights(self):
        origin = self.from_combobox.get()
        destination = self.to_combobox.get()
        date = self.date_entry.get()
        flight_class = self.class_combobox.get()
        N_LIMIT = 200

        try:
            conn = connect_to_replica()
            cursor = conn.cursor(dictionary=True)

            cursor.callproc("GetFlightsBySearch", (origin, destination, date, flight_class))
            results = []
            for result in cursor.stored_results():
                rows = result.fetchall()
                for row in rows:
                    if isinstance(row.get("departure_time"), datetime):
                        row["departure_time"] = row["departure_time"].isoformat()
                    if isinstance(row.get("arrival_time"), datetime):
                        row["arrival_time"] = row["arrival_time"].isoformat()
                    results.append(row)

            if len(results) > N_LIMIT:
                cursor.close()
                cursor = conn.cursor(dictionary=True)
                cursor.callproc("GetFlightsLimited", (origin, destination, date, flight_class))
                results = []
                for result in cursor.stored_results():
                    rows = result.fetchall()
                    for row in rows:
                        if isinstance(row.get("departure_time"), datetime):
                            row["departure_time"] = row["departure_time"].isoformat()
                        if isinstance(row.get("arrival_time"), datetime):
                            row["arrival_time"] = row["arrival_time"].isoformat()
                        results.append(row)

            user_id = self.controller.current_user_id
            redis_key = f"user:{user_id}:search_results"
            redis_client.setex(redis_key, 60, json.dumps(results))

            self.full_results = results
            self.selected_flights.clear()

            airlines = sorted(set(f["airline_name"] for f in results))
            self.airline_filter["values"] = ["All"] + airlines
            self.airline_filter.set("All")

            self.display_results(results)

            cursor.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"Stored procedure error: {e}")

    def display_results(self, results):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for flight in results:
            display_values = (
                "☑" if tuple(flight.values()) in self.selected_flights else "☐",
                flight["flight_id"],
                flight["airline_name"],
                flight["departure_time"],
                flight["arrival_time"],
                flight["class_type"],
                flight["price"]
            )
            self.tree.insert("", "end", values=display_values)

    def apply_filters(self):
        airline = self.airline_filter.get()
        min_price = self.min_price_var.get()
        max_price = self.max_price_var.get()
        time_of_day = self.time_var.get()

        filtered = []
        for flight in self.full_results:
            try:
                match_airline = airline == "All" or flight["airline_name"] == airline

                price = float(flight["price"])
                if min_price and price < float(min_price):
                    continue
                if max_price and price > float(max_price):
                    continue

                if time_of_day:
                    hour = datetime.fromisoformat(flight["departure_time"]).hour
                    if (time_of_day == "Morning" and not 5 <= hour < 12) or \
                       (time_of_day == "Afternoon" and not 12 <= hour < 17) or \
                       (time_of_day == "Evening" and not 17 <= hour < 21) or \
                       (time_of_day == "Night" and not (hour >= 21 or hour < 5)):
                        continue

                if match_airline:
                    filtered.append(flight)
            except Exception:
                continue

        self.display_results(filtered)

    def toggle_selection(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        values = self.tree.item(item_id, "values")
        flight_tuple = values[1:]

        if values[0] == "☐":
            self.tree.item(item_id, values=("☑", *flight_tuple))
            self.selected_flights.add(flight_tuple)
        else:
            self.tree.item(item_id, values=("☐", *flight_tuple))
            self.selected_flights.discard(flight_tuple)

    def show_selected_flights(self):
        user_id = self.controller.current_user_id
        search_key = f"user:{user_id}:search_results"
        selection_key = f"user:{user_id}:selected_flights"

        if not redis_client.exists(search_key):
            messagebox.showwarning("Session Expired", "Your session has expired. Please search for flights again.")
            return

        if not self.selected_flights:
            messagebox.showwarning("No Selection", "Please select at least one flight.")
            return

        try:
            search_results = json.loads(redis_client.get(search_key))
            selected_flights_full = [
                flight for flight in search_results
                if (
                    str(flight["flight_id"]),
                    flight["airline_name"],
                    flight["departure_time"],
                    flight["arrival_time"],
                    flight["class_type"],
                    str(flight["price"])
                ) in self.selected_flights
            ]

            redis_client.setex(selection_key, 60, json.dumps(selected_flights_full))
            self.controller.show_frame("FlightDetailsPage", data=selected_flights_full)

        except Exception as e:
            messagebox.showerror("Redis Error", f"Failed to save selected flights: {e}")
