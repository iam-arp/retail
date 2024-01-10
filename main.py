

import streamlit as st
import pandas as pd
from datetime import datetime
import random
import base64
from reportlab.pdfgen import canvas
import logging
import sqlite3

try:
    # Try importing the required libraries
    import streamlit, pandas, reportlab
except ImportError:
    # If an ImportError occurs, install dependencies
    import subprocess
    subprocess.run(["pip", "install", "-r", "requirements.txt"])

# Configure logging
logging.basicConfig(filename='retail_billing_system.log', level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class SalesDatabase:
    def __init__(self, db_path="sales_database.db"):
        self.db_path = db_path
        self._create_sales_table()

    def _create_sales_table(self):
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    transaction_id TEXT,
                    name TEXT,
                    customer_id TEXT,
                    date TEXT,
                    time TEXT,
                    sku TEXT,
                    quantity INTEGER,
                    price REAL
                )
            ''')

    @staticmethod
    def save_to_database(db_path, transaction_id, name, customer_id, date, time, sku, quantity, price):
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (transaction_id, name, customer_id, date, time, sku, quantity, price))


class InvoiceGenerator:
    def generate_pdf(self, data):
        if not data['Transaction ID']:
            st.error("No data available to generate PDF. Add items to the bill first.")
            return

        pdf_filename = f"invoice_{data['Transaction ID'][0]}.pdf"

        with open(pdf_filename, "wb") as pdf_file:
            c = canvas.Canvas(pdf_file)
            c.setFont("Helvetica", 12)

            c.drawString(200, 800, "Invoice")
            c.drawString(50, 780, f"Transaction ID: {data['Transaction ID'][0]}")
            c.drawString(50, 760, f"Name: {data['Name'][0]}")
            c.drawString(50, 740, f"Date: {data['Date'][0]}")
            c.drawString(50, 720, f"Time: {data['Time'][0]}")
            c.line(50, 710, 550, 710)

            y_position = 680
            c.drawString(50, y_position, "SKU | Quantity | Price")
            y_position -= 20

            for i in range(len(data['SKU'])):
                sku = data['SKU'][i]
                quantity = data['Quantity'][i]
                price = data['Price'][i]
                c.drawString(50, y_position, f"{sku} | {quantity} | {price}")
                y_position -= 20

            total_price = sum(data['Price'])
            c.drawString(50, y_position - 20, f"Total Price: {total_price}")
            c.save()

        st.success(f"PDF generated successfully! [Download PDF]({pdf_filename})")
        logging.info(f"PDF generated for transaction ID: {data['Transaction ID'][0]}")


class RetailBillingSystem:
    transaction_counter = 1

    def __init__(self):
        self.skus = [f"sku_{i}" for i in range(1, 21)]
        self.sku_price_dict = {sku: round(random.uniform(10, 100), 2) for sku in self.skus}
        self.bill_data = {'Transaction ID': [], 'Name': [], 'Customer ID': [], 'Date': [], 'Time': [], 'SKU': [],
                          'Quantity': [], 'Price': []}
        self.sales_db = SalesDatabase()
        self.invoice_generator = InvoiceGenerator()

    @classmethod
    def generate_transaction_id(cls):
        transaction_id = f'TR-{datetime.now().strftime("%Y%m%d%H%M%S")}-{cls.transaction_counter}'
        cls.transaction_counter += 1
        return transaction_id

    def add_to_bill(self, name_or_id, sku, quantity):
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        transaction_id = self.generate_transaction_id()

        self.bill_data['Transaction ID'].append(transaction_id)
        self.bill_data['Name'].append(name_or_id)
        self.bill_data['Customer ID'].append(name_or_id)
        self.bill_data['Date'].append(date)
        self.bill_data['Time'].append(time)
        self.bill_data['SKU'].append(sku)
        self.bill_data['Quantity'].append(quantity)
        price = self.sku_price_dict[sku] * quantity
        self.bill_data['Price'].append(price)

        SalesDatabase.save_to_database(self.sales_db.db_path, transaction_id, name_or_id, name_or_id, date, time, sku,
                                       quantity, price)

        self.display_message(f"Item added to the bill for {name_or_id}", message_type="success")
        logging.info(
            f"Item added to the bill. Transaction ID: {transaction_id}, SKU: {sku}, Quantity: {quantity}, Price: {price}")

    def display_current_bill(self):
        if not self.bill_data['Transaction ID']:
            st.warning("No data available. Add items to the bill first.")
            return

        st.title("Current Bill")
        st.table(pd.DataFrame(self.bill_data))

    def save_data_to_csv(self):
        if not self.bill_data['Transaction ID']:
            st.warning("No data available to save. Add items to the bill first.")
            return

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        csv_filename = f"sales_records_{timestamp}.csv"
        sales_df = pd.DataFrame(self.bill_data)
        sales_df.to_csv(csv_filename, mode='a', header=not st.file_uploader("Upload CSV", type=["csv"]) is not None,
                        index=False)
        self.display_message("Sales data appended to CSV successfully!", message_type="success")
        logging.info(f"Sales data appended to CSV. File: {csv_filename}")

    def download_sales_records_csv(self):
        if not self.bill_data['Transaction ID']:
            st.warning("No data available to download. Add items to the bill first.")
            return

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        csv_filename = f"all_sales_records_{timestamp}.csv"
        sales_df = pd.DataFrame(self.bill_data)
        sales_df.to_csv(csv_filename, index=False)
        self.display_message("All sales records CSV generated. Click below to download.",
                             message_type="success")
        st.markdown(
            self.get_binary_file_downloader_html(csv_filename, 'Download All Sales Records CSV'),
            unsafe_allow_html=True)
        logging.info(
            f"All sales records CSV generated and downloaded. File: {csv_filename}")

    def display_message(self, message, message_type="info"):
        if message_type == "info":
            st.info(message)
        elif message_type == "success":
            st.success(message)
        elif message_type == "warning":
            st.warning(message)
        elif message_type == "error":
            st.error(message)

    def get_binary_file_downloader_html(self, file_path, download_link_text):
        with open(file_path, 'rb') as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<a href="data:file/csv;base64,{b64}" download="{file_path}">{download_link_text}</a>'


def main():
    retail_system = RetailBillingSystem()

    st.title("sky: Retail Billing System")

    st.sidebar.title("GD Vishal Grocery")
    selected_option = st.sidebar.radio("Select an option",
                                       ["Add to Bill", "View Current Bill", "Save Data to CSV", "Generate PDF",
                                        "Download All Sales Records CSV"])

    if selected_option == "Add to Bill":
        st.sidebar.write("Enter customer information and items to add to the bill.")
        name_or_id = st.text_input("Enter Name or Customer ID:")
        sku = st.selectbox("Select SKU:", retail_system.skus)
        quantity = st.number_input("Enter Quantity:", min_value=1, step=1)

        st.info(f"Selected SKU: {sku}, Price: ${retail_system.sku_price_dict[sku]:.2f}")

        if st.button("Add to Bill"):
            retail_system.add_to_bill(name_or_id, sku, quantity)

    elif selected_option == "View Current Bill":
        retail_system.display_current_bill()

    elif selected_option == "Save Data to CSV":
        retail_system.save_data_to_csv()

    elif selected_option == "Generate PDF":
        retail_system.invoice_generator.generate_pdf(retail_system.bill_data)

    elif selected_option == "Download All Sales Records CSV":
        retail_system.download_sales_records_csv()


if __name__ == "__main__":
    main()
