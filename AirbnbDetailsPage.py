import tkinter as tk
from tkinter import ttk, messagebox
import json
import logging
from data_connection import redis_client, connect_to_master

logging.basicConfig(level=logging.INFO)

class AirbnbDetailsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Airbnb Details", font=("Arial", 18)).pack(pady=10)

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True)

        self.columns = (
            "Select", "listing_id", "host_name", "listing_name", "room_type",
            "price", "min_nights", "available_days", "remaining_availability", "nights_to_book"
        )

        self.tree = ttk.Treeview(
            tree_frame,
            columns=self.columns,
            show="headings",
            height=15
        )
        self.tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        for col in self.columns:
            self.tree.heading(col, text=col.replace("_", " ").capitalize())
            self.tree.column(col, width=110, anchor="center")

        self.entry_vars = {}
        self.selected_rows = set()

        self.tree.bind("<ButtonRelease-1>", self.toggle_selection)
        self.tree.bind("<Double-1>", self.edit_cell)

        ttk.Button(self, text="Book Selected Stays", command=self.book_selected_airbnbs).pack(pady=10)
        ttk.Button(self, text="Back", command=lambda: controller.show_frame("AirbnbPage")).pack(pady=5)

        self.remaining_seconds = 0
        self.countdown_label = ttk.Label(self, text="")
        self.countdown_label.pack()

    def update_timer(self):
        if self.remaining_seconds <= 0:
            messagebox.showinfo("Time Expired", "Your Airbnb selection expired. Please reselect.")
            self.controller.show_frame("AirbnbPage")
            return
        self.countdown_label.config(text=f"⏳ Time left: {self.remaining_seconds} seconds")
        self.remaining_seconds -= 1
        self.after(1000, self.update_timer)

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.entry_vars.clear()
        self.selected_rows.clear()

    def load_data(self, data=None):
        self.clear_table()

        user_id = self.controller.current_user_id
        redis_key = f"user:{user_id}:selected_airbnbs"

        try:
            data_json = redis_client.get(redis_key)
            if not data_json:
                messagebox.showinfo("Session Expired", "Your Airbnb selection expired. Please reselect.")
                return

            self.remaining_seconds = 60  
            self.update_timer()

            listings = json.loads(data_json)
            for listing in listings:
                values = (
                    "☐",
                    listing[0],  
                    listing[1],  
                    listing[2],  
                    listing[3],  
                    listing[4],  
                    listing[5],  
                    listing[6],  
                    listing[7],  
                    ""
                )
                item_id = self.tree.insert("", "end", values=values)
                self.entry_vars[item_id] = tk.StringVar()
        except Exception as e:
            logging.error("Redis fetch failed: %s", e)
            messagebox.showerror("Error", f"Could not load data: {e}")

    def toggle_selection(self, event):
        col = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)
        if not row or col != "#1":
            return

        current = self.tree.item(row, "values")
        if current[0] == "☐":
            self.tree.item(row, values=("☑", *current[1:]))
            self.selected_rows.add(row)
        else:
            self.tree.item(row, values=("☐", *current[1:]))
            self.selected_rows.discard(row)

    def edit_cell(self, event):
        col = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)
        if col != "#10" or not row:
            return

        bbox = self.tree.bbox(row, col)
        if not bbox:
            return
        x, y, width, height = bbox
        entry = ttk.Entry(self.tree, textvariable=self.entry_vars[row])
        entry.place(x=x, y=y, width=width, height=height)
        entry.focus()

        def on_focus_out(e):
            entry.destroy()
            self.tree.set(row, column="#10", value=self.entry_vars[row].get())

        entry.bind("<FocusOut>", on_focus_out)

    def book_selected_airbnbs(self):
        if not self.selected_rows:
            messagebox.showwarning("No Selection", "Please select at least one listing to book.")
            return

        bookings = []
        for row_id in self.selected_rows:
            values = self.tree.item(row_id, "values")
            listing_id = values[1]
            price = float(values[5])
            min_nights = int(values[6])
            available_days = int(values[7])
            remaining = int(values[8])

            try:
                nights_to_book = int(self.entry_vars[row_id].get())
            except ValueError:
                messagebox.showwarning("Input Error", f"Invalid night count for listing {listing_id}")
                continue

            if nights_to_book <= 0:
                messagebox.showwarning("Input Error", f"Enter at least 1 night for listing {listing_id}")
                continue
            if nights_to_book < min_nights:
                messagebox.showwarning("Minimum Nights", f"Must book at least {min_nights} nights.")
                continue
            if nights_to_book > remaining:
                messagebox.showwarning("Availability Error", f"Not enough availability for listing {listing_id}")
                continue

            total_price = nights_to_book * price
            bookings.append({
                "listing_id": listing_id,
                "nights": nights_to_book,
                "price": total_price
            })

        if not bookings:
            messagebox.showerror("No Valid Bookings", "No valid bookings made.")
            return

        user_id = self.controller.current_user_id
        redis_key = f"user:{user_id}:airbnb_bookings"
        redis_client.setex(redis_key, 300, json.dumps(bookings))  

        success = 0
        for b in bookings:
            if book_airbnb_nights(b["listing_id"], b["nights"], b["price"], user_id):
                success += 1

        if success == 0:
            messagebox.showerror("Failure", "All bookings failed.")
        else:
            messagebox.showinfo("Success", f"{success} booking(s) successful.")

def book_airbnb_nights(listing_id, nights, total_price, user_id):
    conn = connect_to_master()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        conn.start_transaction()

        cursor.execute("""
            SELECT availability_id, availability_365, remaining_availability
            FROM availability
            WHERE listing_id = %s
            FOR UPDATE SKIP LOCKED
        """, (listing_id,))
        row = cursor.fetchone()
        if not row:
            raise Exception("Availability not found or locked by another user.")

        availability_id, available, remaining = row
        if nights > remaining:
            raise Exception("Not enough days available.")

        cursor.execute("""
            UPDATE availability
            SET availability_365 = availability_365 - %s,
                remaining_availability = remaining_availability - %s
            WHERE availability_id = %s AND remaining_availability >= %s
        """, (nights, nights, availability_id, nights))

        if cursor.rowcount == 0:
            raise Exception("Availability update failed due to concurrency.")

        cursor.execute("""
            INSERT INTO booking (user_id, status)
            VALUES (%s, 'confirmed')
        """, (user_id,))
        booking_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO booking_details
            (booking_id, item_id, item_type, quantity, price, number_of_days)
            VALUES (%s, %s, 'airbnb', 1, %s, %s)
        """, (booking_id, listing_id, total_price, nights))

        conn.commit()
        return True
    except Exception as e:
        logging.error("Booking failed: %s", e, exc_info=True)
        messagebox.showerror("Booking Error", str(e))
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
