import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from data_connection import connect_to_replica


class BookingPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_rows = set()

        ttk.Label(self, text="My Bookings", font=("Arial", 18)).pack(pady=10)

        filter_frame = ttk.Frame(self)
        filter_frame.pack(pady=5)

    
        ttk.Label(filter_frame, text="Date from:").grid(row=0, column=0, padx=5)
        self.from_entry = ttk.Entry(filter_frame, width=12)
        self.from_entry.grid(row=0, column=1)

        ttk.Label(filter_frame, text="Date to:").grid(row=0, column=2, padx=5)
        self.to_entry = ttk.Entry(filter_frame, width=12)
        self.to_entry.grid(row=0, column=3)

        ttk.Label(filter_frame, text="Status:").grid(row=0, column=4, padx=5)
        self.status_cb = ttk.Combobox(filter_frame, values=["", "confirmed", "cancelled"], width=12)
        self.status_cb.grid(row=0, column=5)

        ttk.Label(filter_frame, text="Type:").grid(row=0, column=6, padx=5)
        self.type_cb = ttk.Combobox(filter_frame, values=["", "flight", "airbnb", "flight & airbnb"], width=15)
        self.type_cb.grid(row=0, column=7)

        ttk.Button(filter_frame, text="Apply Filters", command=self.load_bookings).grid(row=0, column=8, padx=10)

        
        columns = ["Select", "Booking ID", "Booking Date", "Status", "Type", "Item ID", "Price", "Quantity"]
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=20)
        self.tree.pack(fill="both", expand=True)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90 if col != "Select" else 60, anchor="center")

    
        self.tree.bind("<Button-1>", self.handle_click)

        ttk.Button(self, text="Back", command=lambda: controller.show_frame("TravelerPage")).pack(pady=10)

    def load_data(self):
        
        self.load_bookings()

    def load_bookings(self):
        user_id = self.controller.current_user_id
        if not user_id:
            messagebox.showerror("Error", "User not logged in.")
            return

        from_date = self.from_entry.get().strip()
        to_date = self.to_entry.get().strip()
        status = self.status_cb.get()
        btype = self.type_cb.get()

        sql = """
            SELECT b.bookingid, b.booking_date, b.status, bd.item_type,
                   bd.item_id, bd.price, bd.quantity
            FROM booking b
            JOIN booking_details bd ON b.bookingid = bd.booking_id
            WHERE b.user_id = %s
        """
        params = [user_id]

        if from_date:
            sql += " AND b.booking_date >= %s"
            params.append(from_date)

        if to_date:
            sql += " AND b.booking_date <= %s"
            params.append(to_date)

        if status:
            sql += " AND b.status = %s"
            params.append(status)

        if btype:
            if btype == "flight & airbnb":
                sql += " AND bd.item_type IN ('flight', 'airbnb')"
            else:
                sql += " AND bd.item_type = %s"
                params.append(btype)

        try:
            conn = connect_to_replica()
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            results = cursor.fetchall()

        
            for row in self.tree.get_children():
                self.tree.delete(row)
            self.selected_rows.clear()

            
            for row in results:
                tree_row = ("☐",) + row  
                row_id = self.tree.insert("", "end", values=tree_row)

            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def handle_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.tree.identify_column(event.x)
        if column != "#1":  
            return

        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return

        current_value = self.tree.set(row_id, "Select")
        if current_value == "☐":
            self.tree.set(row_id, "Select", "✔")
            self.selected_rows.add(row_id)
        else:
            self.tree.set(row_id, "Select", "☐")
            self.selected_rows.discard(row_id)
