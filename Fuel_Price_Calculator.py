#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import io

# Set custom CSS for background color and layout
st.markdown(
    """
    <style>
    .stApp {
        background-color: #aacfc0;
    }
    .section {
        padding: 20px 0;
        border-top: 2px solid #195a3e;
        margin-top: 20px;
    }
    .centered {
        display: flex;
        justify-content: center;
    }
    table th {
        text-align: center !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Add a company logo
st.image("KF.png", width=600)

# Set the title of the app
st.title("Fuel Price Estimate")

# Section 1: Product Type and Province
st.markdown("<div class='section'><h3>Section 1: Product and Province</h3></div>", unsafe_allow_html=True)
product_col, province_col = st.columns(2)
product = product_col.selectbox("Product Type (mandatory): ▼", ["", "Clear Diesel", "Dyed Diesel"])
provinces = [
    "", "Alberta", "British Columbia", "Manitoba", "New Brunswick",
    "Newfoundland & Labrador", "Northwest Territories", "Nova Scotia",
    "Ontario", "Prince Edward Island", "Quebec", "Saskatchewan", "Yukon"
]
province = province_col.selectbox("Choose your province (mandatory): ▼", provinces)

# Section 2: Tax Exemptions
st.markdown("<div class='section'><h3>Section 2: Tax Exemptions</h3></div>", unsafe_allow_html=True)
excise_col, carbon_col, provincial_col = st.columns(3)
excise_tax_exemption = excise_col.selectbox("Federal Excise Tax Exemption ▼", ["", "Yes", "No"])
carbon_tax_exemption = carbon_col.selectbox("Federal Carbon Tax Exemption ▼", ["", "Yes", "No"])
provincial_tax_exemption = provincial_col.selectbox("Provincial Fuel Tax Exemption ▼", ["", "Yes", "No"])

# Section 3: Price, Differential, Trucking, and Volume
st.markdown("<div class='section'><h3>Section 3: Price and Volume Details</h3></div>", unsafe_allow_html=True)
price_col, differential_col, trucking_col, volume_col = st.columns(4)
product_price = price_col.number_input("Product Price:", min_value=0.0, value=0.0, step=0.01)
differential = differential_col.number_input("Differential:", value=0.0, step=0.01, format="%.2f")
trucking_cost = trucking_col.number_input("Trucking:", value=0.0, step=0.01, format="%.2f")
volume = volume_col.number_input("Volume (liters):", min_value=0, value=1)

# Calculation logic
federal_excise_tax = None
federal_carbon_tax = None
provincial_fuel_tax = None

# Calculate taxes based on exemptions
if excise_tax_exemption == "No":
    federal_excise_tax = 0.04
elif excise_tax_exemption == "Yes":
    federal_excise_tax = 0

if carbon_tax_exemption == "No":
    federal_carbon_tax = 0.2139
elif carbon_tax_exemption == "Yes":
    federal_carbon_tax = 0

# Calculate provincial fuel tax based on conditions
if provincial_tax_exemption == "Yes":
    provincial_fuel_tax = 0
else:
    if province == "":
        provincial_fuel_tax = None
    elif province == "Alberta":
        provincial_fuel_tax = 0.04 if product == "Dyed Diesel" else 0.13
    elif province == "British Columbia":
        provincial_fuel_tax = 0.03 if product == "Dyed Diesel" else 0.2267
    elif province == "Manitoba":
        provincial_fuel_tax = 0.03 if product == "Dyed Diesel" else 0.18
    elif province == "New Brunswick":
        provincial_fuel_tax = 0.03 if product == "Dyed Diesel" else 0.232
    elif province == "Newfoundland & Labrador":
        provincial_fuel_tax = 0.03 if product == "Dyed Diesel" else 0.205
    elif province == "Northwest Territories":
        provincial_fuel_tax = 0.031 if product == "Dyed Diesel" else 0.131
    elif province == "Nova Scotia":
        provincial_fuel_tax = 0.03 if product == "Dyed Diesel" else 0.194
    elif province == "Ontario":
        provincial_fuel_tax = 0.045 if product == "Dyed Diesel" else 0.183
    elif province == "Prince Edward Island":
        provincial_fuel_tax = 0.03 if product == "Dyed Diesel" else 0.242
    elif province == "Quebec":
        provincial_fuel_tax = 0.03 if product == "Dyed Diesel" else 0.202
    elif province == "Saskatchewan":
        provincial_fuel_tax = 0.09 if product == "Dyed Diesel" else 0.19
    elif province == "Yukon":
        provincial_fuel_tax = 0.062 if product == "Dyed Diesel" else 0.112

# Calculate final price with tax
product_price_with_tax = (
    product_price + (federal_excise_tax or 0) + 
    (federal_carbon_tax or 0) + (provincial_fuel_tax or 0) + 
    differential + trucking_cost
)

# Calculate subtotal and total with GST
subtotal = product_price_with_tax * volume
gst = subtotal * 0.05
total_price = subtotal + gst

# Display results in a structured format
st.markdown("<div class='section'><h3 style='text-align: center;'>Estimated Price</h3></div>", unsafe_allow_html=True)

results_table_data = {
    'Description': [
        'Product Price', 'Federal Excise Tax', 'Federal Carbon Tax', 'Provincial Fuel Tax',
        'Differential', 'Trucking', 'Product Price w/Tax', 'Volume', 'Subtotal', 'GST @ 5%', 'Total'
    ],
    'Amount': [
        f"${product_price:.2f}",
        f"${federal_excise_tax:.2f}" if federal_excise_tax is not None else "",
        f"${federal_carbon_tax:.2f}" if federal_carbon_tax is not None else "",
        f"${provincial_fuel_tax:.2f}" if provincial_fuel_tax is not None else "",
        f"${differential:.2f}", f"${trucking_cost:.2f}", f"${product_price_with_tax:.2f}",
        f"{volume} liters", f"${subtotal:.2f}", f"${gst:.2f}", f"<b>${total_price:.2f}</b>"
    ]
}

results_df = pd.DataFrame(results_table_data)

# Display the results as a centered table
st.markdown(
    f"""
    <div style="display: flex; flex-direction: column; align-items: center;">
        <div style="width: 35%;">
            {results_df.to_html(index=False, escape=False)}
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

# Add button to save results as Excel
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
    return output.getvalue()

# Center the "Save Results to Excel" button
st.markdown(
    """
    <div style="display: flex; justify-content: center; margin-top: 20px;">
        <div style="width: 35%;">
    """, 
    unsafe_allow_html=True
)

if st.button('Save Results to Excel'):
    excel_data = to_excel(results_df)
    st.download_button(
        label="Click here to download",
        data=excel_data,
        file_name="fuel_price_calculation.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.markdown("</div></div>", unsafe_allow_html=True)



# In[ ]:




