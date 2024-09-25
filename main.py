import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang import Builder
import sqlite3
import smtplib
from email.mime.text import MIMEText
import os
from random import randint
import random
import matplotlib.pyplot as plt


# Placeholder for RFID tracking
def get_rfid_data():
    try:
        # Simulate RFID data
        return {"item1": "Aisle 4", "item2": "Aisle 7", "item3": "Aisle 12"}
    except Exception as e:
        print(f"Error retrieving RFID data: {e}")
        return {}


# Placeholder for sensor readings (temperature, humidity, etc.)
def get_sensor_data():
    try:
        return {"temperature": 22, "humidity": 50, "weight": random.uniform(10, 50)}
    except Exception as e:
        print(f"Error retrieving sensor data: {e}")
        return {}


# Email alert system
def send_alert_via_email(message):
    sender = "inventory.alerts@example.com"
    receiver = "user@example.com"
    msg = MIMEText(message)
    msg["Subject"] = "Inventory Alert"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        smtp = smtplib.SMTP('smtp.example.com')
        smtp.sendmail(sender, [receiver], msg.as_string())
        smtp.quit()
        print("Alert sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


# Initialize the database
def init_db():
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            item_name TEXT,
                            stock INTEGER,
                            condition TEXT,
                            image_path TEXT
                        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS suppliers (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            supplier_name TEXT,
                            contact_info TEXT
                        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS reports (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            report_date TEXT,
                            report_details TEXT
                        )''')

        conn.commit()
        conn.close()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")


# Inventory Screen
class InventoryScreen(Screen):
    def check_alerts(self):
        try:
            conn = sqlite3.connect('inventory.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM inventory WHERE stock < 5")
            low_stock_items = cursor.fetchall()
            conn.close()

            if low_stock_items:
                alert_text = "\n".join([f"Item: {item[1]}, Stock: {item[2]}" for item in low_stock_items])
                self.show_popup("Low Stock Alert", alert_text)
                send_alert_via_email(alert_text)
            else:
                self.show_popup("No Alerts", "All inventory items are sufficiently stocked.")
        except Exception as e:
            print(f"Error checking alerts: {e}")

    def show_popup(self, title, content):
        try:
            popup = Popup(title=title, content=Label(text=content), size_hint=(0.75, 0.5))
            popup.open()
        except Exception as e:
            print(f"Error showing popup: {e}")

    def real_time_rfid_tracking(self):
        try:
            rfid_data = get_rfid_data()
            rfid_map = "\n".join([f"{item}: {location}" for item, location in rfid_data.items()])
            self.show_popup("Real-Time RFID Tracking", rfid_map)
        except Exception as e:
            print(f"Error in RFID tracking: {e}")


class SupplierScreen(Screen):
    supplier_name = None
    supplier_contact = None

    def add_supplier(self):
        try:
            name = self.supplier_name.text
            contact = self.supplier_contact.text

            if name and contact:
                conn = sqlite3.connect('inventory.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO suppliers (supplier_name, contact_info) VALUES (?, ?)", (name, contact))
                conn.commit()
                conn.close()

                self.show_popup("Success", "Supplier added successfully.")
                self.supplier_name.text = ""
                self.supplier_contact.text = ""
            else:
                self.show_popup("Error", "Please enter both supplier name and contact information.")
        except Exception as e:
            print(f"Error adding supplier: {e}")

    def show_popup(self, title, content):
        try:
            popup = Popup(title=title, content=Label(text=content), size_hint=(0.75, 0.5))
            popup.open()
        except Exception as e:
            print(f"Error showing popup: {e}")


class AnalyticsScreen(Screen):
    def generate_graphs(self):
        try:
            items = ["Item A", "Item B", "Item C", "Item D"]
            stock = [20, 15, 7, 3]

            plt.bar(items, stock)
            plt.xlabel('Items')
            plt.ylabel('Stock')
            plt.title('Stock Levels of Inventory')
            plt.show()
        except Exception as e:
            print(f"Error generating graphs: {e}")

    def show_popup(self, title, content):
        try:
            popup = Popup(title=title, content=Label(text=content), size_hint=(0.75, 0.5))
            popup.open()
        except Exception as e:
            print(f"Error showing popup: {e}")


class DailyReportScreen(Screen):
    def generate_daily_report(self):
        try:
            self.show_popup("Daily Report", "Generating daily inventory report...")
        except Exception as e:
            print(f"Error generating daily report: {e}")

    def show_popup(self, title, content):
        try:
            popup = Popup(title=title, content=Label(text=content), size_hint=(0.75, 0.5))
            popup.open()
        except Exception as e:
            print(f"Error showing popup: {e}")


class ImportExportScreen(Screen):
    def export_data(self):
        try:
            self.show_popup("Export Data", "Exporting inventory data...")
        except Exception as e:
            print(f"Error exporting data: {e}")

    def import_data(self):
        try:
            self.show_popup("Import Data", "Importing data from external sources...")
        except Exception as e:
            print(f"Error importing data: {e}")

    def show_popup(self, title, content):
        try:
            popup = Popup(title=title, content=Label(text=content), size_hint=(0.75, 0.5))
            popup.open()
        except Exception as e:
            print(f"Error showing popup: {e}")


class WindowManager(ScreenManager):
    pass


class InventoryApp(App):
    def build(self):
        try:
            init_db()  # Initialize database
            sm = WindowManager()
            
            # Add screens to the ScreenManager
            sm.add_widget(InventoryScreen(name='inventory'))
            sm.add_widget(SupplierScreen(name='supplier'))
            sm.add_widget(AnalyticsScreen(name='analytics'))
            sm.add_widget(DailyReportScreen(name='daily_report'))
            sm.add_widget(ImportExportScreen(name='import_export'))

            sm.current = 'inventory'  # Set initial screen to 'inventory'
            return sm
        except Exception as e:
            print(f"Error during app build: {e}")


if __name__ == "__main__":
    try:
        InventoryApp().run()
    except Exception as e:
        print(f"Error running the app: {e}")
