import tkinter as tk
from tkinter import ttk, messagebox
import json
from data_connection import redis_client, connect_to_replica

class AirbnbPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Search Airbnb Listings", font=("Arial", 18)).pack(pady=10)

        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="City:").grid(row=0, column=0, padx=5, pady=5)
        self.city_combobox = ttk.Combobox(form_frame, width=30)
        self.city_combobox.grid(row=0, column=1, padx=5)

        ttk.Label(form_frame, text="Room Type:").grid(row=0, column=2, padx=5, pady=5)
        self.room_type_combobox = ttk.Combobox(
            form_frame, values=["", "Entire home/apt", "Private room", "Shared room"]
        )
        self.room_type_combobox.grid(row=0, column=3, padx=5)

        ttk.Label(form_frame, text="Minimum Nights:").grid(row=1, column=0, padx=5, pady=5)
        self.min_nights_entry = ttk.Entry(form_frame)
        self.min_nights_entry.grid(row=1, column=1, padx=5)

        ttk.Button(self, text="Search", command=self.search_airbnbs).pack(pady=10)

        # 🔍 Filter controls
        filter_frame = ttk.LabelFrame(self, text="Filters (Redis)")
        filter_frame.pack(pady=5, fill="x", padx=10)

        ttk.Label(filter_frame, text="Host Name:").grid(row=0, column=0, padx=5, pady=5)
        self.host_name_filter = ttk.Entry(filter_frame, width=20)
        self.host_name_filter.grid(row=0, column=1)

        ttk.Label(filter_frame, text="Max Price:").grid(row=0, column=2, padx=5, pady=5)
        self.max_price_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.max_price_var, width=10).grid(row=0, column=3)

        ttk.Label(filter_frame, text="Min Nights ≥").grid(row=1, column=0, padx=5, pady=5)
        self.min_nights_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.min_nights_var, width=10).grid(row=1, column=1)

        ttk.Label(filter_frame, text="Available Days ≥").grid(row=1, column=2, padx=5, pady=5)
        self.available_days_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.available_days_var, width=10).grid(row=1, column=3)

        ttk.Label(filter_frame, text="Remaining Availability ≥").grid(row=1, column=4, padx=5, pady=5)
        self.remaining_avail_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.remaining_avail_var, width=10).grid(row=1, column=5)

        ttk.Button(filter_frame, text="Apply Filters", command=self.apply_redis_filters).grid(row=0, column=4, padx=10)

        self.columns = (
            "Select", "listing_id", "host_name", "listing_name", "room_type",
            "price", "min_nights", "available_days", "remaining_availability"
        )

        self.tree = ttk.Treeview(self, columns=self.columns, show="headings", height=15)
        self.tree.pack(fill="both", expand=True)

        for col in self.columns:
            self.tree.heading(col, text=col.replace("_", " ").capitalize())
            self.tree.column(col, anchor="center", width=110)

        self.tree.bind("<ButtonRelease-1>", self.toggle_selection)

        ttk.Button(self, text="Confirm Selection", command=self.confirm_selection).pack(pady=10)
        ttk.Button(self, text="Back", command=lambda: controller.show_frame("TravelerPage")).pack(pady=5)

        self.selected_rows = set()
        self.load_cities()

    def load_cities(self):
        try:
            conn = connect_to_replica()
            cursor = conn.cursor()
            cursor.execute("SELECT city_name FROM cities")
            cities = [row[0] for row in cursor.fetchall()]
            self.city_combobox["values"] = cities
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load cities: {e}")

    def search_airbnbs(self):
        city = self.city_combobox.get()
        room_type = self.room_type_combobox.get()
        min_nights = self.min_nights_entry.get()

        if not city:
            messagebox.showwarning("Input Error", "Please select a city.")
            return

        try:
            min_nights = int(min_nights) if min_nights else 0
        except ValueError:
            messagebox.showwarning("Input Error", "Minimum nights must be a number.")
            return

        try:
            conn = connect_to_replica()
            cursor = conn.cursor()
            sql = """
                SELECT 
                    l.listing_id, h.host_name, l.listing_name, l.room_type, 
                    p.price, p.minimum_nights, a.availability_365, a.remaining_availability
                FROM listings l
                JOIN hosts h ON l.host_id = h.host_id
                JOIN pricing p ON l.listing_id = p.listing_id
                JOIN availability a ON l.listing_id = a.listing_id
                JOIN cities c ON l.city_id = c.city_id
                WHERE c.city_name = %s
            """
            params = [city]

            if room_type:
                sql += " AND l.room_type = %s"
                params.append(room_type)
            if min_nights:
                sql += " AND p.minimum_nights >= %s"
                params.append(min_nights)

            cursor.execute(sql, tuple(params))
            results = cursor.fetchall()
            cursor.close()
            conn.close()

            redis_key = f"user:{self.controller.current_user_id}:airbnb_search_results"
            redis_client.setex(redis_key, 60, json.dumps(results))

            for row in self.tree.get_children():
                self.tree.delete(row)
            self.selected_rows.clear()

            for listing in results:
                self.tree.insert("", "end", values=("☐", *listing))

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def apply_redis_filters(self):
        user_id = self.controller.current_user_id
        redis_key = f"user:{user_id}:airbnb_search_results"

        if not redis_client.exists(redis_key):
            messagebox.showwarning("Session Expired", "Your session has expired. Please search again.")
            return

        try:
            search_results = json.loads(redis_client.get(redis_key))

            host_name = self.host_name_filter.get().strip().lower()
            max_price = self.max_price_var.get().strip()
            min_nights = self.min_nights_var.get().strip()
            available_days = self.available_days_var.get().strip()
            remaining_avail = self.remaining_avail_var.get().strip()

            filtered = []
            for row in search_results:
                try:
                    host_match = host_name in row[1].lower() if host_name else True
                    price_match = float(row[4]) <= float(max_price) if max_price else True
                    nights_match = int(row[5]) >= int(min_nights) if min_nights else True
                    avail_match = int(row[6]) >= int(available_days) if available_days else True
                    remaining_match = int(row[7]) >= int(remaining_avail) if remaining_avail else True

                    if host_match and price_match and nights_match and avail_match and remaining_match:
                        filtered.append(row)
                except:
                    continue

            for item in self.tree.get_children():
                self.tree.delete(item)
            self.selected_rows.clear()

            for listing in filtered:
                self.tree.insert("", "end", values=("☐", *listing))

        except Exception as e:
            messagebox.showerror("Filter Error", f"Failed to apply filters: {e}")

    def toggle_selection(self, event):
        row_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not row_id or col != "#1":
            return

        values = self.tree.item(row_id, "values")
        if values[0] == "☐":
            self.tree.item(row_id, values=("☑", *values[1:]))
            self.selected_rows.add(row_id)
        else:
            self.tree.item(row_id, values=("☐", *values[1:]))
            self.selected_rows.discard(row_id)

    def confirm_selection(self):
        user_id = self.controller.current_user_id
        redis_key = f"user:{user_id}:selected_airbnbs"
        search_key = f"user:{user_id}:airbnb_search_results"

        if not redis_client.exists(search_key):
            messagebox.showwarning("Session Expired", "Your Airbnb session has expired. Please search again.")
            return

        if not self.selected_rows:
            messagebox.showwarning("No Selection", "Please select at least one listing.")
            return

        try:
            search_results = json.loads(redis_client.get(search_key))
            selected_values = [self.tree.item(row_id, "values")[1:] for row_id in self.selected_rows]

            selected_airbnbs_full = [
                listing for listing in search_results
                if tuple(map(str, listing)) in selected_values
            ]

            redis_client.setex(redis_key, 60, json.dumps(selected_airbnbs_full))
            self.controller.show_frame("AirbnbDetailsPage", data=selected_airbnbs_full)

        except Exception as e:
            messagebox.showerror("Redis Error", f"Failed to save selected listings: {e}")
