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
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from io import BytesIO
import sqlite3
import random
import hashlib
import smtplib
from email.mime.text import MIMEText
import matplotlib.pyplot as plt
import pandas as pd
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
    try:
        smtp_server = 'smtp.example.com'  # Replace with actual server
        smtp_port = 587  # Replace with actual port
        sender_email = "your_email@example.com"
        sender_password = "your_password"
        recipient_email = "recipient_email@example.com"

        msg = MIMEText(message)
        msg['Subject'] = 'Inventory Alert'
        msg['From'] = sender_email
        msg['To'] = recipient_email

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()

        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Hash passwords for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # Create the users, inventory, contracts, and logs tables as usual
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'  -- Assuming a default role
                    )''')

    # Check and modify the suppliers table if necessary
    try:
        cursor.execute('''ALTER TABLE suppliers ADD COLUMN performance_rating INTEGER''')
    except sqlite3.OperationalError:
        # Column already exists
        pass

    try:
        cursor.execute('''ALTER TABLE suppliers ADD COLUMN order_history TEXT''')
    except sqlite3.OperationalError:
        # Column already exists
        pass

    try:
        cursor.execute('''ALTER TABLE suppliers ADD COLUMN bidding_price REAL''')
    except sqlite3.OperationalError:
        # Column already exists
        pass

    conn.commit()
    conn.close()

def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return any(column[1] == column_name for column in cursor.fetchall())

def load_suppliers():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # List of suppliers with optional columns
    suppliers = [
        ("Supplier 1", "supplier1@example.com", "100 orders", 5, 1000.00),
        ("Supplier 2", "supplier2@example.com", "200 orders", 4, 1100.00),
        ("Supplier 3", "supplier3@example.com", "150 orders", 4, 1200.00),
        ("Supplier 4", "supplier4@example.com", "250 orders", 3, 950.00)
    ]

    # Check for columns before inserting
    for supplier in suppliers:
        query = "INSERT INTO suppliers (supplier_name, contact"
        values = [supplier[0], supplier[1]]
        
        if column_exists(cursor, 'suppliers', 'order_history'):
            query += ", order_history"
            values.append(supplier[2])
        
        if column_exists(cursor, 'suppliers', 'performance_rating'):
            query += ", performance_rating"
            values.append(supplier[3])
        
        if column_exists(cursor, 'suppliers', 'bidding_price'):
            query += ", bidding_price"
            values.append(supplier[4])

        query += ") VALUES (" + ', '.join(['?'] * len(values)) + ")"
        cursor.execute(query, values)

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
        query = "INSERT INTO inventory (item_name"
        values = [item[0]]
        
        # Check if 'stock' column exists
        if column_exists(cursor, 'inventory', 'stock'):
            query += ", stock"
            values.append(item[1])
        
        # Check if 'condition' column exists
        if column_exists(cursor, 'inventory', 'condition'):
            query += ", condition"
            values.append(item[2])
        
        # Check if 'rfid_tag' column exists
        if column_exists(cursor, 'inventory', 'rfid_tag'):
            query += ", rfid_tag"
            values.append(item[3])
        
        query += ") VALUES (" + ', '.join(['?'] * len(values)) + ")"
        cursor.execute(query, values)

    conn.commit()
    conn.close()

# Report generation with sample historical data
def generate_reports():
    # Adjust this to use only the columns you know exist
    data = {
        'Date': [datetime.now() - timedelta(days=i) for i in range(4)],
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


# Base Screen class with reusable popup
class BaseScreen(Screen):
    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content), size_hint=(0.75, 0.5))
        popup.open()

# Login Screen
class LoginScreen(BaseScreen):
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

# Register Screen
class RegisterScreen(BaseScreen):
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

# Inventory Management Screen
class ManageInventoryScreen(BaseScreen):
    def add_item(self):
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        item_name = self.ids.item_name.text
        stock = self.ids.stock.text
        condition = self.ids.condition.text
        rfid_tag = self.ids.rfid_tag.text
        
        try:
            cursor.execute("INSERT INTO inventory (item_name, stock, condition, rfid_tag) VALUES (?, ?, ?, ?)",
                           (item_name, stock, condition, rfid_tag))
            conn.commit()
            self.show_popup("Item Added", "Item has been added successfully!")
        except sqlite3.Error as e:
            self.show_popup("Error", str(e))
        finally:
            conn.close()

    def view_inventory(self):
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory")
        items = cursor.fetchall()
        conn.close()
        
        # Display items in some UI component
        # Assuming you have a ListView or similar widget to show items
        # For demonstration, we'll just print the items
        for item in items:
            print(item)

# Main App class
class InventoryApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(ManageInventoryScreen(name='inventory'))
        return sm

if __name__ == '__main__':
    init_db()
    load_suppliers()
    load_sample_inventory()
    InventoryApp().run()
