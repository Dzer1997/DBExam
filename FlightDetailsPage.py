import tkinter as tk
from tkinter import ttk, messagebox
import json
import logging
from data_connection import redis_client, connect_to_master  

logging.basicConfig(level=logging.INFO)

class FlightDetailsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Flight Details", font=("Arial", 18)).pack(pady=10)

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Select", "flight_id", "airline", "departure_time", "arrival_time",
                     "class_type", "price", "seats_remaining", "seats_to_book"),
            show="headings"
        )
        self.tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col.replace("_", " ").capitalize())
            self.tree.column(col, width=130, anchor="center")

        self.seat_entries = {}
        self.selected_rows = set()

        self.tree.bind("<ButtonRelease-1>", self.toggle_selection)
        self.tree.bind("<Double-1>", self.edit_cell)

        ttk.Button(self, text="Book Selected Flights", command=self.book_selected_flights).pack(pady=10)
        ttk.Button(self, text="Back", command=lambda: controller.show_frame("PlaneTicketPage")).pack(pady=5)

    def load_data(self, data):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.seat_entries.clear()
        self.selected_rows.clear()

        for flight in data:
            values = (
                "☐",
                flight.get("flight_id"),
                flight.get("airline_name"),
                flight.get("departure_time"),
                flight.get("arrival_time"),
                flight.get("class_type"),
                flight.get("price"),
                flight.get("seats_remaining", 0),
                ""
            )
            item_id = self.tree.insert("", "end", values=values)
            self.seat_entries[item_id] = tk.StringVar()

    def toggle_selection(self, event):
        region = self.tree.identify_region(event.x, event.y)
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

        if col != "#9" or not row:
            return

        bbox = self.tree.bbox(row, col)
        if not bbox:
            return

        x, y, width, height = bbox
        entry = ttk.Entry(self.tree, textvariable=self.seat_entries[row])
        entry.place(x=x, y=y, width=width, height=height)
        entry.focus()

        def on_focus_out(e):
            entry.destroy()
            self.tree.set(row, column="#9", value=self.seat_entries[row].get())

        entry.bind("<FocusOut>", on_focus_out)

    def book_selected_flights(self):
        if not self.selected_rows:
            messagebox.showwarning("No Selection", "Please select at least one flight to book.")
            return

        booked = []
        for row_id in self.selected_rows:
            values = self.tree.item(row_id, "values")
            try:
                seats_to_book = int(self.seat_entries[row_id].get())
            except ValueError:
                messagebox.showwarning("Input Error", f"Invalid seat count for flight {values[1]}")
                continue

            flight_id = values[1]
            class_type = values[5]
            available = int(values[7])
            if seats_to_book <= 0:
                messagebox.showwarning("Input Error", f"Please enter at least 1 seat for flight {flight_id}.")
                continue
            if seats_to_book > available:
                messagebox.showwarning("Seat Error", f"Not enough seats for flight {flight_id}.")
                continue

            booked.append({
                "flight_id": flight_id,
                "class_type": class_type,
                "seats": seats_to_book
            })

        if not booked:
            messagebox.showerror("No Valid Bookings", "No valid bookings were made. Please check your seat input.")
            return

        user_id = self.controller.current_user_id
        redis_key = f"user:{user_id}:pending_bookings"
        redis_client.setex(redis_key, 60, json.dumps(booked))

        success_count = 0
        for b in booked:
            if book_flight_seats(b["flight_id"], b["class_type"], b["seats"], user_id):
                success_count += 1

        if success_count == 0:
            messagebox.showerror("Failure", "All bookings failed. Please try again.")
        else:
            messagebox.showinfo("Booking Result", f"{success_count} flight(s) booked successfully.")

def book_flight_seats(flight_id, class_type, seats_to_book, user_id):
    conn = connect_to_master()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        conn.start_transaction()

        logging.info(f"Booking {seats_to_book} seat(s) for Flight ID {flight_id}, Class {class_type}")

        cursor.execute("""
            SELECT classes_id, seats_remaining, price
            FROM flights_classes
            WHERE flight_id = %s AND LOWER(class_type) = LOWER(%s)
            FOR UPDATE
        """, (flight_id, class_type))
        row = cursor.fetchone()
        if not row:
            raise Exception("Flight class not found.")

        class_id, current_seats, seat_price = row
        logging.info(f"[DEBUG] Seats before update: {current_seats}")

        if seats_to_book > current_seats:
            raise Exception("Not enough seats available.")

        total_price = seat_price * seats_to_book

    
        cursor.execute("""
            UPDATE flights_classes
            SET seats_remaining = seats_remaining - %s
            WHERE classes_id = %s AND seats_remaining >= %s
        """, (seats_to_book, class_id, seats_to_book))

        if cursor.rowcount == 0:
            raise Exception("Seat update failed due to concurrent modification.")

    
        cursor.execute("""
            SELECT seats_remaining FROM flights_classes
            WHERE classes_id = %s
        """, (class_id,))
        updated_seats = cursor.fetchone()[0]
        logging.info(f"[DEBUG] Seats after update: {updated_seats}")

        cursor.execute("""
            INSERT INTO booking (user_id, status)
            VALUES (%s, 'confirmed')
        """, (user_id,))
        booking_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO booking_details
            (booking_id, item_id, item_type, quantity, price, number_of_seats)
            VALUES (%s, %s, 'flight', 1, %s, %s)
        """, (booking_id, class_id, total_price, seats_to_book))

        conn.commit()
        logging.info(f"Booking successful. Total: {total_price}")
        return True

    except Exception as e:
        logging.error("Booking failed: %s", e, exc_info=True)
        messagebox.showerror("Booking Error", str(e))
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
