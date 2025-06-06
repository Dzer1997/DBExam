import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
from data_connection import get_mongo_client, redis_client  # Your DB connection module


class PackagesPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.full_results = []
        self.selected_packages = set()

        ttk.Label(self, text="Travel Packages", font=("Arial", 20)).pack(pady=10)

        # Filter section
        filter_frame = ttk.Frame(self)
        filter_frame.pack(pady=10)

        ttk.Label(filter_frame, text="To (City):").grid(row=0, column=0, padx=5)
        self.city_to_entry = ttk.Entry(filter_frame)
        self.city_to_entry.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Max Price:").grid(row=0, column=2, padx=5)
        self.max_price_entry = ttk.Entry(filter_frame)
        self.max_price_entry.grid(row=0, column=3, padx=5)

        ttk.Button(filter_frame, text="Search", command=self.search_packages).grid(row=0, column=4, padx=5)

        # Treeview for packages
        self.tree = ttk.Treeview(self, columns=(
            "package_id", "city_from", "city_to", "flight_date",
            "price", "category", "guest_satisfaction_overall"
        ), show="headings", selectmode="extended")
        self.tree.pack(fill="both", expand=True, pady=10)

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col.replace("_", " ").title())

        self.tree.bind("<ButtonRelease-1>", self.toggle_selection)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Show Selected", command=self.show_selected_packages).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Back", command=lambda: controller.show_frame("TravelerPage")).pack(side="left", padx=5)

    def search_packages(self):
        city_to = self.city_to_entry.get().strip()
        max_price = self.max_price_entry.get().strip()
        client = get_mongo_client()
        if not client:
            messagebox.showerror("Connection Error", "Failed to connect to MongoDB.")
            return

        try:
            db = client["main_db"]
            collection = db["packages"]

            query = {}
            if city_to:
                query["city_to"] = {"$regex": f"^{city_to}", "$options": "i"}
            if max_price:
                try:
                    query["price"] = {"$lte": float(max_price)}
                except ValueError:
                    messagebox.showwarning("Invalid Input", "Please enter a valid number for price.")
                    return

            projection = {
                "_id": 0,
                "package_id": 1,
                "city_from": 1,
                "city_to": 1,
                "flight_date": 1,
                "price": 1,
                "category": 1,
                "guest_satisfaction_overall": 1
            }

            cursor = collection.find(query, projection).limit(100)
            results = list(cursor)
            for r in results:
                if isinstance(r.get("flight_date"), datetime):
                    r["flight_date"] = r["flight_date"].strftime("%Y-%m-%d")

            user_id = getattr(self.controller, 'current_user_id', 'guest')
            redis_key = f"user:{user_id}:package_results"
            redis_client.setex(redis_key, 60, json.dumps(results))

            self.full_results = results
            self.selected_packages.clear()
            self.display_results(results)
        except Exception as e:
            messagebox.showerror("Query Error", str(e))

    def display_results(self, results):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for pkg in results:
            values = (
                pkg.get("package_id", ""),
                pkg.get("city_from", ""),
                pkg.get("city_to", ""),
                pkg.get("flight_date", ""),
                pkg.get("price", ""),
                pkg.get("category", ""),
                pkg.get("guest_satisfaction_overall", "")
            )
            self.tree.insert("", "end", values=values)

    def toggle_selection(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        values = self.tree.item(item_id, "values")
        if values in self.selected_packages:
            self.selected_packages.discard(values)
        else:
            self.selected_packages.add(values)

    def show_selected_packages(self):
        user_id = getattr(self.controller, 'current_user_id', 'guest')
        redis_key = f"user:{user_id}:package_results"
        selection_key = f"user:{user_id}:selected_packages"

        if not redis_client.exists(redis_key):
            messagebox.showwarning("Session Expired", "Your session has expired. Please search again.")
            return
        if not self.selected_packages:
            messagebox.showinfo("No Selection", "Please select at least one package.")
            return

        try:
            all_results = json.loads(redis_client.get(redis_key))
            selected_full = [
                pkg for pkg in all_results
                if (
                    str(pkg.get("package_id", "")),
                    pkg.get("city_from", ""),
                    pkg.get("city_to", ""),
                    pkg.get("flight_date", ""),
                    str(pkg.get("price", "")),
                    pkg.get("category", ""),
                    str(pkg.get("guest_satisfaction_overall", ""))
                ) in self.selected_packages
            ]
            redis_client.setex(selection_key, 60, json.dumps(selected_full))
            self.controller.show_frame("PackageDetailsPage", data=selected_full)
        except Exception as e:
            messagebox.showerror("Redis Error", str(e))
