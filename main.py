

import streamlit as st
import pandas as pd
from datetime import datetime
import random
import base64
from reportlab.pdfgen import canvas

try:
    # Try importing the required libraries
    import streamlit, pandas, reportlab
except ImportError:
    # If an ImportError occurs, install dependencies
    import subprocess
    subprocess.run(["pip", "install", "-r", "requirements.txt"])

class RetailBillingSystem:
    def __init__(self):
        self.skus = [f"sku_{i}" for i in range(1, 21)]
        self.sku_price_dict = {sku: round(random.uniform(10, 100), 2) for sku in self.skus}
        self.bill_data = {'Transaction ID': [], 'Name': [], 'Customer ID': [], 'Date': [], 'Time': [], 'SKU': [], 'Quantity': [], 'Price': []}
        self.transaction_counter = 1

    def generate_transaction_id(self):
        transaction_id = f'TR-{datetime.now().strftime("%Y%m%d%H%M%S")}-{self.transaction_counter}'
        self.transaction_counter += 1
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
        self.bill_data['Price'].append(self.sku_price_dict[sku] * quantity)

        st.success(f"Item added to the bill for {name_or_id}")

    def generate_pdf(self, data):
        pdf_filename = f"invoice_{data['Transaction ID']}.pdf"

        with open(pdf_filename, "wb") as pdf_file:
            c = canvas.Canvas(pdf_file)
            c.setFont("Helvetica", 12)

            c.drawString(200, 800, "Invoice")
            c.drawString(50, 780, f"Transaction ID: {data['Transaction ID']}")
            c.drawString(50, 760, f"Name: {data['Name']}")
            c.drawString(50, 740, f"Date: {data['Date']}")
            c.drawString(50, 720, f"Time: {data['Time']}")
            c.line(50, 710, 550, 710)

            y_position = 680
            for key, value in data.items():
                if key in ('Transaction ID', 'Name', 'Date', 'Time'):
                    continue
                c.drawString(50, y_position, f"{key}: {value}")
                y_position -= 20

            total_price = sum(data['Price'])
            c.drawString(50, y_position - 20, f"Total Price: {total_price}")
            c.save()

        st.success(f"PDF generated successfully! [Download PDF]({pdf_filename})")

    def display_current_bill(self):
        st.table(pd.DataFrame(self.bill_data))

    def save_data_to_csv(self):
        sales_df = pd.DataFrame(self.bill_data)
        sales_df.to_csv("sales_records.csv", index=False)
        st.success("Sales data saved to CSV successfully!")

    def download_sales_records_csv(self):
        sales_df = pd.DataFrame(self.bill_data)
        sales_df.to_csv("all_sales_records.csv", index=False)
        st.success("All sales records CSV generated. Click below to download.")
        st.markdown(self.get_binary_file_downloader_html('all_sales_records.csv', 'Download All Sales Records CSV'), unsafe_allow_html=True)

    def get_binary_file_downloader_html(self, file_path, download_link_text):
        with open(file_path, 'rb') as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        return f'<a href="data:file/csv;base64,{b64}" download="{file_path}">{download_link_text}</a>'

def main():
    retail_system = RetailBillingSystem()

    st.title("Retail Billing System")

    name_or_id = st.text_input("Enter Name or Customer ID:")
    sku = st.selectbox("Select SKU:", retail_system.skus)
    quantity = st.number_input("Enter Quantity:", min_value=1, step=1)

    st.info(f"Selected SKU: {sku}, Price: ${retail_system.sku_price_dict[sku]:.2f}")

    if st.button("Add to Bill"):
        retail_system.add_to_bill(name_or_id, sku, quantity)

    if st.button("View Current Bill"):
        retail_system.display_current_bill()

    if st.button("Save Data to CSV"):
        retail_system.save_data_to_csv()

    if st.button("Generate PDF"):
        retail_system.generate_pdf(retail_system.bill_data)

    if st.button("Download All Sales Records CSV"):
        retail_system.download_sales_records_csv()

if __name__ == "__main__":
    main()

