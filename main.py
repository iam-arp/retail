

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import random

try:
    # Try importing the required libraries
    import streamlit, pandas, fpdf
except ImportError:
    # If an ImportError occurs, install dependencies
    import subprocess
    subprocess.run(["pip", "install", "-r", "requirements.txt"])

# Generate SKUs and random prices
skus = [f"sku_{i}" for i in range(1, 21)]
prices = [round(random.uniform(10, 100), 2) for _ in range(20)]
sku_price_dict = dict(zip(skus, prices))

# Initialize data structure to store the billing information
bill_data = {'Transaction ID': [], 'Name': [], 'Customer ID': [], 'Date': [], 'Time': [], 'SKU': [], 'Quantity': [], 'Price': []}
transaction_counter = 1

# Function to generate PDF from bill_data
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Invoice", ln=True, align='C')
    pdf.ln(10)

    total_price = 0

    for key, value in data.items():
        if key == 'SKU':
            continue
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
        if key == 'Price':
            total_price += value

    pdf.cell(200, 10, txt=f"Total Price: {total_price}", ln=True)

    pdf.output(f"invoice_{data['Transaction ID']}.pdf")

# Streamlit app
def main():
    global transaction_counter  # Keep track of the transaction ID

    st.title("Retail Billing System")

    # Input fields
    name_or_id = st.text_input("Enter Name or Customer ID:")
    sku = st.selectbox("Select SKU:", skus)
    quantity = st.number_input("Enter Quantity:", min_value=1, step=1)

    # Display selected SKU and its price
    st.info(f"Selected SKU: {sku}, Price: ${sku_price_dict[sku]:.2f}")

    # Add to bill_data on button click
    if st.button("Add to Bill"):
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        bill_data['Transaction ID'].append(transaction_counter)
        bill_data['Name'].append(name_or_id)
        bill_data['Customer ID'].append(name_or_id)
        bill_data['Date'].append(date)
        bill_data['Time'].append(time)
        bill_data['SKU'].append(sku)
        bill_data['Quantity'].append(quantity)
        bill_data['Price'].append(sku_price_dict[sku] * quantity)

        # Increment transaction ID
        transaction_counter += 1  
        st.success(f"Item added to the bill for {name_or_id}")

    # Display the current bill_data
    if st.button("View Current Bill"):
        st.table(pd.DataFrame(bill_data))

    # Save data to CSV on button click
    if st.button("Save Data to CSV"):
        sales_df = pd.DataFrame(bill_data)
        sales_df.to_csv("sales_records.csv", index=False)
        st.success("Sales data saved to CSV successfully!")

    # Generate PDF on button click
    if st.button("Generate PDF"):
        generate_pdf(bill_data)
        st.success("PDF generated successfully!")

    # Download CSV button
    if st.button("Download All Sales Records CSV"):
        sales_df = pd.DataFrame(bill_data)
        sales_df.to_csv("all_sales_records.csv", index=False)
        st.success("All sales records CSV generated. Click below to download.")
        st.markdown(get_binary_file_downloader_html('all_sales_records.csv', 'Download All Sales Records CSV'), unsafe_allow_html=True)

# Function to create a download link for a file
def get_binary_file_downloader_html(file_path, download_link_text):
    with open(file_path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{file_path}">{download_link_text}</a>'

if __name__ == "__main__":
    main()
