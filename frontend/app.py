
import streamlit as st
import pandas as pd
import joblib
import numpy as np
import requests # requests is needed for the Streamlit app to call the backend API
import os

# Base URL of the Flask backend
BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:7860")

# Set the title of the Streamlit app
st.title("SuperKart Sales Revenue Forecasting")

# Section for online forecasting
st.subheader("Online Forecasting")

# Collect user input for product features
weight = st.number_input("Product Weight", value=12.66)
sugar = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
area = st.number_input("Product Allocated Area", value=0.027)
mrp = st.number_input("Product MRP", value=117.08)
size = st.selectbox("Store Size", ["Small", "Medium", "High"])
city = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
store_type = st.selectbox("Store Type", ["Departmental Store", "Supermarket Type 1", "Supermarket Type 2", "Food Mart"])
pid_char = st.selectbox("Product Id Char (e.g., FD)", ["FD", "NC", "DR"])
age = st.number_input("Store Age Years", value=16)
cat = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])

# Convert user input into a DataFrame
input_data = pd.DataFrame([{
    'Product_Weight': weight,
    'Product_Sugar_Content': sugar,
    'Product_Allocated_Area': area,
    'Product_MRP': mrp,
    'Store_Size': size,
    'Store_Location_City_Type': city,
    'Store_Type': store_type,
    'Product_Id_char': pid_char,
    'Store_Age_Years': age,
    'Product_Type_Category': cat,
  }])

# Make forecast when the "Forecast" button is clicked
if st.button("Forecast", type="primary"):
    response = requests.post(f"{BACKEND_URL}/v1/sales", json=input_data.to_dict(orient='records')[0])  # Send data to Flask API
    if response.status_code == 200:
        forecast = response.json()['Forecasted Sales Revenue (in dollars)']
        st.success(f"Forecasted Sales Revenue (in dollars): {forecast}")
    else:
        st.error("Unable to connect to the prediction API.")

# Section for batch forecasting
st.subheader("Batch Forecasting")

# Allow users to upload a CSV file for batch forecasting
uploaded_file = st.file_uploader("Upload CSV file for batch forecasting", type=["csv"])

# Make batch forecast when the "Forecast Batch" button is clicked
if uploaded_file is not None:
    if st.button("Forecast Batch", type="primary"):
        response = requests.post(f"{BACKEND_URL}/v1/salesbatch", files={"file": uploaded_file})  # Send file to Flask API
        if response.status_code == 200:
            forecasts = response.json()
            st.success("Batch forecasting completed!")
            st.write(forecasts)  # Display the forecasts
        else:
            st.error("Unable to connect to the forecasting API.")
