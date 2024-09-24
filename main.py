import os
import sqlite3
import pandas as pd
import random
from datetime import datetime
from threading import Thread
import time
import matplotlib.pyplot as plt
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from pyzbar.pyzbar import decode
from PIL import Image

# Database setup
DB_PATH = "inventory.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

conn = get_db_connection()
c = conn.cursor()

# Create tables
def initialize_db():
    c.execute('''CREATE TABLE IF NOT EXISTS inventory
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  item_name TEXT NOT NULL,
                  quantity INTEGER NOT NULL,
                  price REAL NOT NULL,
                  location TEXT NOT NULL,
                  condition TEXT NOT NULL,
                  last_updated TEXT NOT NULL,
                  barcode TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS suppliers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  supplier_name TEXT NOT NULL,
                  contact TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS stock_movements
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  item_id INTEGER,
                  movement_type TEXT,
                  quantity INTEGER,
                  timestamp TEXT,
                  FOREIGN KEY(item_id) REFERENCES inventory(id))''')
    conn.commit()

initialize_db()

# Barcode scanning function
def scan_barcode(image_path):
    try:
        image = Image.open(image_path)
        barcodes = decode(image)
        if barcodes:
            return barcodes[0].data.decode('utf-8')
        else:
            show_popup("Error", "No barcode detected.")
            return None
    except Exception as e:
        show_popup("Error", f"Barcode scanning failed: {str(e)}")
        return None

# RFID scanning placeholder function
def scan_rfid():
    return "RFID123456"  # Simulated RFID tag for demo purposes

# Helper function to display popups
def show_popup(title, message):
    popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
    popup_label = Label(text=message)
    close_button = Button(text="Close", size_hint=(1, 0.3))
    popup_layout.add_widget(popup_label)
    popup_layout.add_widget(close_button)
    popup = Popup(title=title, content=popup_layout, size_hint=(0.6, 0.4))
    close_button.bind(on_press=popup.dismiss)
    popup.open()

# Inventory management screen
class InventoryScreen(Screen):
    def add_item(self):
        item_name = self.ids.item_name.text.strip()
        quantity = self.ids.quantity.text.strip()
        price = self.ids.price.text.strip()
        barcode_input = self.ids.barcode.text.strip()
        location = self.ids.location.text.strip()
        condition = self.ids.condition.text.strip()

<<<<<<< HEAD
        if not item_name or not quantity.isdigit() or not price or not location or not condition:
            show_popup("Error", "All fields are required.")
            return

        barcode = barcode_input or scan_barcode("barcode_image.png")
        if not barcode:
            show_popup("Error", "Barcode is required.")
            return

        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            c.execute("""INSERT INTO inventory (item_name, quantity, price, location, condition, last_updated, barcode)
                         VALUES (?, ?, ?, ?, ?, ?, ?)""",
                      (item_name, int(quantity), float(price), location, condition, last_updated, barcode))
            conn.commit()
            show_popup("Success", "Item added successfully.")
            self.clear_fields()
            App.get_running_app().root.current = "view_inventory"
        except sqlite3.IntegrityError:
            show_popup("Error", "Barcode already exists.")
=======
            # Input validation
            if item_name and quantity.isdigit() and price.replace('.', '', 1).isdigit():
                c.execute("INSERT INTO inventory (item_name, quantity, price, location, condition, last_updated) VALUES (?, ?, ?, ?, ?, ?)", 
                          (item_name, int(quantity), float(price), location, condition, last_updated))
                conn.commit()
                show_popup("Success", "Item Added Successfully")
                self.ids.item_name.text = ''
                self.ids.quantity.text = ''
                self.ids.price.text = ''

            else:
                show_popup("Error", "Invalid Input. Ensure quantity is a number and price is a valid decimal.")
>>>>>>> 6c44879c553f0fd5a422195abae2fae4bc676411
        except Exception as e:
            show_popup("Error", f"Failed to add item: {str(e)}")

    def clear_fields(self):
        self.ids.item_name.text = ""
        self.ids.quantity.text = ""
        self.ids.price.text = ""
        self.ids.barcode.text = ""
        self.ids.location.text = ""
        self.ids.condition.text = ""

    def import_excel(self):
        try:
            data = pd.read_excel("inventory_import.xlsx")
            for _, row in data.iterrows():
                c.execute("""INSERT INTO inventory 
                             (item_name, quantity, price, location, condition, last_updated, barcode) 
                             VALUES (?, ?, ?, ?, ?, ?, ?)""",
                          (row['item_name'], int(row['quantity']), float(row['price']),
                           row['location'], row['condition'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"), row['barcode']))
            conn.commit()
            show_popup("Success", "Inventory imported successfully.")
        except Exception as e:
            show_popup("Error", f"Failed to import inventory: {str(e)}")

    def export_excel(self):
        try:
            c.execute("SELECT * FROM inventory")
            data = c.fetchall()
            df = pd.DataFrame(data, columns=["id", "item_name", "quantity", "price", "location", "condition", "last_updated", "barcode"])
            df.to_excel("inventory_export.xlsx", index=False)
            show_popup("Success", "Inventory exported successfully.")
        except Exception as e:
            show_popup("Error", f"Failed to export inventory: {str(e)}")

    def scan_rfid_tag(self):
        Thread(target=self._scan_rfid_thread).start()

    def _scan_rfid_thread(self):
        rfid = scan_rfid()
        if rfid:
            c.execute("SELECT * FROM inventory WHERE barcode = ?", (rfid,))
            item = c.fetchone()
            if item:
                Clock.schedule_once(lambda dt: self.populate_fields(item))
            else:
                Clock.schedule_once(lambda dt: show_popup("Error", "No item found with this RFID tag."))

    def populate_fields(self, item):
        self.ids.item_name.text = item[1]
        self.ids.quantity.text = str(item[2])
        self.ids.price.text = str(item[3])
        self.ids.location.text = item[4]
        self.ids.condition.text = item[5]
        self.ids.barcode.text = item[7]

# View inventory screen
class ViewInventoryScreen(Screen):
    def on_enter(self):
        self.load_inventory()

    def load_inventory(self):
        self.ids.inventory_container.clear_widgets()
        try:
            c.execute("SELECT * FROM inventory")
            items = c.fetchall()
            for item in items:
                item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
                item_label = Label(text=f"{item[1]} | Qty: {item[2]} | Price: ${item[3]:.2f} | Location: {item[4]} | Condition: {item[5]} | Barcode: {item[7]}")
                edit_button = Button(text="Edit", size_hint_x=0.1)
                delete_button = Button(text="Delete", size_hint_x=0.1)
                edit_button.bind(on_press=lambda btn, item_id=item[0]: self.edit_item(item_id))
                delete_button.bind(on_press=lambda btn, item_id=item[0]: self.delete_item(item_id))
                item_layout.add_widget(item_label)
                item_layout.add_widget(edit_button)
                item_layout.add_widget(delete_button)
                self.ids.inventory_container.add_widget(item_layout)
        except Exception as e:
            show_popup("Error", f"Failed to load inventory: {str(e)}")

    def edit_item(self, item_id):
        show_popup("Info", f"Edit functionality for item ID {item_id} is not implemented yet.")

    def delete_item(self, item_id):
        try:
            c.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
            conn.commit()
            show_popup("Success", "Item deleted successfully.")
            self.load_inventory()
        except Exception as e:
            show_popup("Error", f"Failed to delete item: {str(e)}")

# Supplier management screen
class SupplierManagement(Screen):
    def add_supplier(self):
        supplier_name = self.ids.supplier_name.text.strip()
        supplier_contact = self.ids.supplier_contact.text.strip()

        if not supplier_name or not supplier_contact:
            show_popup("Error", "All fields are required.")
            return

        try:
            c.execute("INSERT INTO suppliers (supplier_name, contact) VALUES (?, ?)", (supplier_name, supplier_contact))
            conn.commit()
            show_popup("Success", "Supplier added successfully.")
            self.clear_fields()
            self.load_suppliers()
        except Exception as e:
            show_popup("Error", f"Failed to add supplier: {str(e)}")

    def clear_fields(self):
        self.ids.supplier_name.text = ""
        self.ids.supplier_contact.text = ""

    def on_enter(self):
        self.load_suppliers()

    def load_suppliers(self):
        self.ids.suppliers_container.clear_widgets()
        try:
            c.execute("SELECT * FROM suppliers")
            suppliers = c.fetchall()
            for supplier in suppliers:
                supplier_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
                supplier_label = Label(text=f"{supplier[1]} | Contact: {supplier[2]}")
                delete_button = Button(text="Delete", size_hint_x=0.2)
                delete_button.bind(on_press=lambda btn, supplier_id=supplier[0]: self.delete_supplier(supplier_id))
                supplier_layout.add_widget(supplier_label)
                supplier_layout.add_widget(delete_button)
                self.ids.suppliers_container.add_widget(supplier_layout)
        except Exception as e:
            show_popup("Error", f"Failed to load suppliers: {str(e)}")

    def delete_supplier(self, supplier_id):
        try:
            c.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
            conn.commit()
            show_popup("Success", "Supplier deleted successfully.")
            self.load_suppliers()
        except Exception as e:
            show_popup("Error", f"Failed to delete supplier: {str(e)}")

# Analytics dashboard screen
class DashboardScreen(Screen):
    def on_enter(self):
        self.load_dashboard()

    def load_dashboard(self):
        self.ids.dashboard_container.clear_widgets()
        try:
            c.execute("SELECT SUM(quantity), SUM(quantity * price) FROM inventory")
            total_items, total_value = c.fetchone()

            total_items_label = Label(text=f"Total Items in Inventory: {total_items}")
            total_value_label = Label(text=f"Total Inventory Value: ${total_value:.2f}")

            self.ids.dashboard_container.add_widget(total_items_label)
            self.ids.dashboard_container.add_widget(total_value_label)

            self.plot_pie_chart()
        except Exception as e:
            show_popup("Error", f"Failed to load dashboard: {str(e)}")

    def plot_pie_chart(self):
        c.execute("SELECT item_name, quantity FROM inventory")
        data = c.fetchall()
        labels = [item[0] for item in data]
        quantities = [item[1] for item in data]

        plt.figure(figsize=(6, 6))
        plt.pie(quantities, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title("Stock Distribution by Item")
        plt.savefig("stock_distribution.png")
        self.ids.pie_chart.source = "stock_distribution.png"

# Main app class
class InventoryApp(App):
    def build(self):
        return Builder.load_file("inventory.kv")

# Run the app
if __name__ == "__main__":
    InventoryApp().run()
