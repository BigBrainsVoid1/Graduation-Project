from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.lang import Builder
import sqlite3
import pandas as pd
import random
from datetime import datetime
import matplotlib.pyplot as plt
from kivy.uix.boxlayout import BoxLayout

# Database connection setup
conn = sqlite3.connect("inventory.db")
c = conn.cursor()

# Create tables if they do not exist
c.execute('''CREATE TABLE IF NOT EXISTS inventory
             (item_name TEXT, quantity INTEGER, price REAL, location TEXT, condition TEXT, last_updated TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS suppliers
             (supplier_name TEXT, contact TEXT)''')
conn.commit()

# Helper function to show popups
def show_popup(title, message):
    popup = Popup(title=title, content=Label(text=message), size_hint=(0.6, 0.3))
    popup.open()

# Inventory Management with Real-Time Monitoring
class InventoryScreen(Screen):
    def add_item(self):
        try:
            item_name = self.ids.item_name.text
            quantity = self.ids.quantity.text
            price = self.ids.price.text
            location = "Warehouse 1"  # Can be dynamic for multi-location
            condition = "New"
            last_updated = str(datetime.now())

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
        except Exception as e:
            show_popup("Error", f"Failed to Add Item: {str(e)}")

    def import_excel(self):
        try:
            data = pd.read_excel("inventory_import.xlsx")
            for index, row in data.iterrows():
                c.execute("INSERT INTO inventory (item_name, quantity, price, location, condition, last_updated) VALUES (?, ?, ?, ?, ?, ?)", 
                          (row['item_name'], row['quantity'], row['price'], row['location'], row['condition'], str(datetime.now())))
            conn.commit()
            show_popup("Success", "Inventory Imported")
        except FileNotFoundError:
            show_popup("Error", "File not found. Make sure 'inventory_import.xlsx' exists.")
        except Exception as e:
            show_popup("Error", f"Failed to Import: {str(e)}")
    
    def export_excel(self):
        try:
            c.execute("SELECT * FROM inventory")
            data = c.fetchall()
            df = pd.DataFrame(data, columns=["item_name", "quantity", "price", "location", "condition", "last_updated"])
            df.to_excel("inventory_export.xlsx", index=False)
            show_popup("Success", "Inventory Exported")
        except Exception as e:
            show_popup("Error", f"Failed to Export: {str(e)}")

    def analyze_stock(self):
        try:
            # Generate a sales trend report using matplotlib
            c.execute("SELECT item_name, SUM(quantity) FROM inventory GROUP BY item_name")
            data = c.fetchall()
            if not data:
                show_popup("Error", "No data available for analysis.")
                return

            item_names = [x[0] for x in data]
            quantities = [x[1] for x in data]

            plt.bar(item_names, quantities)
            plt.xlabel("Item Names")
            plt.ylabel("Total Stock Quantity")
            plt.title("Inventory Stock Analysis")
            plt.show()
        except Exception as e:
            show_popup("Error", f"Failed to Analyze Stock: {str(e)}")

class SupplierManagement(Screen):
    def add_supplier(self):
        try:
            supplier_name = self.ids.supplier_name.text
            supplier_contact = self.ids.supplier_contact.text

            if supplier_name and supplier_contact:
                c.execute("INSERT INTO suppliers (supplier_name, contact) VALUES (?, ?)", (supplier_name, supplier_contact))
                conn.commit()
                show_popup("Success", "Supplier Added Successfully")
            else:
                show_popup("Error", "Invalid Input. Please enter both supplier name and contact.")
        except Exception as e:
            show_popup("Error", f"Failed to Add Supplier: {str(e)}")

class ViewInventoryScreen(Screen):
    def on_enter(self):
        try:
            self.ids.inventory_container.clear_widgets()
            c.execute("SELECT * FROM inventory")
            items = c.fetchall()
            if not items:
                show_popup("Info", "No items found in the inventory.")
                return

            for item in items:
                item_label = Label(text=f"{item[0]} - {item[1]} units - ${item[2]} - {item[3]} - {item[4]} - Last Updated: {item[5]}")
                self.ids.inventory_container.add_widget(item_label)
        except Exception as e:
            show_popup("Error", f"Failed to Load Inventory: {str(e)}")

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.add_widget(self.layout)
        self.update_dashboard()

    def update_dashboard(self):
        try:
            self.layout.clear_widgets()
            c.execute("SELECT item_name, quantity FROM inventory")
            items = c.fetchall()

            summary_label = Label(text=f"Total Items: {len(items)}")
            self.layout.add_widget(summary_label)

            if not items:
                show_popup("Info", "No inventory data available.")
                return

            item_names = [x[0] for x in items]
            quantities = [x[1] for x in items]

            # Create a pie chart of inventory distribution
            plt.figure(figsize=(10, 6))
            plt.pie(quantities, labels=item_names, autopct='%1.1f%%')
            plt.title("Inventory Distribution")
            plt.show()
        except Exception as e:
            show_popup("Error", f"Failed to Update Dashboard: {str(e)}")

class MyInventoryApp(App):
    def build(self):
        try:
            return Builder.load_file('inventory.kv')
        except Exception as e:
            show_popup("Error", f"Failed to Load App: {str(e)}")

if __name__ == '__main__':
    MyInventoryApp().run()
