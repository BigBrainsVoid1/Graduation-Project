import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.scrollview import ScrollView
import sqlite3
import random
import hashlib
import smtplib
from email.mime.text import MIMEText
import matplotlib.pyplot as plt
import pandas as pd
from kivy.uix.widget import Widget
from kivy.clock import Clock
from io import BytesIO
import csv
from datetime import datetime, timedelta

# Placeholder for RFID tracking (optional hardware)
def get_rfid_data():
    return {"item1": "Aisle 4", "item2": "Aisle 7", "item3": "Aisle 12"}

# Placeholder for sensor readings (optional hardware)
def get_sensor_data():
    return {"temperature": 22, "humidity": 50, "weight": random.uniform(10, 50)}

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

# Hash passwords for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize the database
def init_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        role TEXT DEFAULT 'user'
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_name TEXT,
                        stock INTEGER,
                        condition TEXT,
                        rfid_tag TEXT UNIQUE
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS suppliers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        supplier_name TEXT,
                        contact TEXT,
                        order_history TEXT,
                        performance_rating INTEGER,
                        bidding_price REAL
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS contracts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        supplier_id INTEGER,
                        status TEXT,
                        contract_date DATE
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        action TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )''')

    conn.commit()
    conn.close()

# Load suppliers with random data
def load_suppliers():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    suppliers = [
        ("Supplier 1", "supplier1@example.com", "100 orders", 5, 1000.00),
        ("Supplier 2", "supplier2@example.com", "200 orders", 4, 1100.00),
        ("Supplier 3", "supplier3@example.com", "150 orders", 4, 1200.00),
        ("Supplier 4", "supplier4@example.com", "250 orders", 3, 950.00)
    ]

    for supplier in suppliers:
        cursor.execute("INSERT INTO suppliers (supplier_name, contact, order_history, performance_rating, bidding_price) VALUES (?, ?, ?, ?, ?)", supplier)

    conn.commit()
    conn.close()

# Security log function
def log_user_action(user_id, action):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (user_id, action) VALUES (?, ?)", (user_id, action))
    conn.commit()
    conn.close()

# Load sample data into the inventory for reports
def load_sample_inventory():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    inventory_data = [
        ("TV Screen", 100, "New", "RFID_100TV"),
        ("Computer", 1000, "New", "RFID_1000PC"),
        ("Laptop", 200, "Used", "RFID_200LAP"),
        ("Smartphone", 500, "New", "RFID_500PHONE")
    ]

    for item in inventory_data:
        cursor.execute("INSERT INTO inventory (item_name, stock, condition, rfid_tag) VALUES (?, ?, ?, ?)", item)

    conn.commit()
    conn.close()

# Report generation with sample historical data
def generate_reports():
    dates = [datetime.now() - timedelta(days=30*i) for i in range(4)]
    data = {
        'Date': dates,
        'TV Screens': [100, 85, 75, 60],
        'Computers': [1000, 950, 900, 850],
        'Laptops': [200, 180, 150, 120],
        'Smartphones': [500, 480, 450, 400]
    }
    
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    df.plot(ax=ax)
    plt.title("Inventory Levels Over Time")
    plt.ylabel("Number of Items")
    plt.savefig('report_graph.png')
    return df

# Login Screen
class LoginScreen(Screen):
    def login_user(self):
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        username = self.ids.username.text
        password = hash_password(self.ids.password.text)
        cursor.execute("SELECT id, role FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.manager.current = 'inventory'
            log_user_action(user[0], 'Login')
        else:
            self.show_popup("Login Failed", "Invalid username or password")

    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content), size_hint=(0.75, 0.5))
        popup.open()

# Register Screen
class RegisterScreen(Screen):
    def register_user(self):
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        username = self.ids.reg_username.text
        password = hash_password(self.ids.reg_password.text)
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            self.manager.current = 'login'
        except sqlite3.IntegrityError:
            self.show_popup("Registration Failed", "Username already exists")

    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content), size_hint=(0.75, 0.5))
        popup.open()

# Inventory Management Screen (Unified Manage Inventory Page)
class ManageInventoryScreen(Screen):
    def add_item(self):
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        item_name = self.ids.item_name.text
        stock = self.ids.stock.text
        condition = self.ids.condition.text
        rfid_tag = self.ids.rfid_tag.text
        cursor.execute("INSERT INTO inventory (item_name, stock, condition, rfid_tag) VALUES (?, ?, ?, ?)", (item_name, stock, condition, rfid_tag))
        conn.commit()
        conn.close()
        self.show_popup("Success", "Item added successfully")

    def view_items(self):
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory")
        items = cursor.fetchall()
        conn.close()

        content = ScrollView()
        layout = GridLayout(cols=1, padding=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        for item in items:
            item_label = Label(text=f"ID: {item[0]} | Name: {item[1]} | Stock: {item[2]} | Condition: {item[3]} | RFID: {item[4]}")
            layout.add_widget(item_label)
        content.add_widget(layout)

        popup = Popup(title="Inventory Items", content=content, size_hint=(0.85, 0.75))
        popup.open()

    def search_item(self):
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        item_name = self.ids.search_input.text
        cursor.execute("SELECT * FROM inventory WHERE item_name=?", (item_name,))
        item = cursor.fetchone()
        conn.close()

        if item:
            self.show_popup("Item Found", f"ID: {item[0]} | Name: {item[1]} | Stock: {item[2]} | Condition: {item[3]} | RFID: {item[4]}")
        else:
            self.show_popup("Item Not Found", "No item found with that name")

    def import_items(self, path):
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()

        with open(path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cursor.execute("INSERT INTO inventory (item_name, stock, condition, rfid_tag) VALUES (?, ?, ?, ?)", (row['item_name'], row['stock'], row['condition'], row['rfid_tag']))

        conn.commit()
        conn.close()
        self.show_popup("Success", "Items imported successfully")

    def export_items(self):
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory")
        items = cursor.fetchall()

        with open('inventory_export.csv', 'w', newline='') as csvfile:
            fieldnames = ['ID', 'Item Name', 'Stock', 'Condition', 'RFID Tag']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in items:
                writer.writerow({'ID': item[0], 'Item Name': item[1], 'Stock': item[2], 'Condition': item[3], 'RFID Tag': item[4]})

        conn.close()
        self.show_popup("Success", "Items exported successfully")

    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content), size_hint=(0.75, 0.5))
        popup.open()

# Supplier Marketplace Screen
class SupplierMarketplaceScreen(Screen):
    def load_suppliers(self):
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suppliers")
        suppliers = cursor.fetchall()
        conn.close()

        content = ScrollView()
        layout = GridLayout(cols=1, padding=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        for supplier in suppliers:
            supplier_info = f"Name: {supplier[1]} | Contact: {supplier[2]} | History: {supplier[3]} | Rating: {supplier[4]} | Bidding Price: {supplier[5]}"
            supplier_label = Label(text=supplier_info)
            layout.add_widget(supplier_label)

        content.add_widget(layout)
        popup = Popup(title="Supplier Marketplace", content=content, size_hint=(0.85, 0.75))
        popup.open()

    def approve_best_supplier(self):
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suppliers ORDER BY bidding_price ASC LIMIT 1")
        best_supplier = cursor.fetchone()

        if best_supplier:
            cursor.execute("INSERT INTO contracts (supplier_id, status, contract_date) VALUES (?, ?, ?)", (best_supplier[0], 'Approved', datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
            self.show_popup("Success", f"Contract approved with: {best_supplier[1]}")
        else:
            self.show_popup("No Suppliers", "No suppliers found")

        conn.close()

    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content), size_hint=(0.75, 0.5))
        popup.open()

# Reporting Screen
class ReportingScreen(Screen):
    def generate_reports(self):
        df = generate_reports()
        data_view = ScrollView()
        layout = GridLayout(cols=1, padding=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        for index, row in df.iterrows():
            report_label = Label(text=f"Date: {index.date()} | TV Screens: {row['TV Screens']} | Computers: {row['Computers']} | Laptops: {row['Laptops']} | Smartphones: {row['Smartphones']}")
            layout.add_widget(report_label)
        data_view.add_widget(layout)

        report_graph = Widget()
        img = BytesIO(open("report_graph.png", 'rb').read())
        report_image = Image(texture=ImageLoaderPygame().load(img))
        layout.add_widget(report_image)

        popup = Popup(title="Inventory Report", content=data_view, size_hint=(0.85, 0.75))
        popup.open()

    def print_report(self):
        # Placeholder logic for printing
        self.show_popup("Print Report", "Report sent to printer successfully!")

    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content), size_hint=(0.75, 0.5))
        popup.open()

# Main Application Class
class InventoryApp(App):
    def build(self):
        init_db()
        load_suppliers()
        load_sample_inventory()

        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(ManageInventoryScreen(name='inventory'))
        sm.add_widget(SupplierMarketplaceScreen(name='suppliers'))
        sm.add_widget(ReportingScreen(name='reporting'))

        return sm

if __name__ == '__main__':
    InventoryApp().run()
