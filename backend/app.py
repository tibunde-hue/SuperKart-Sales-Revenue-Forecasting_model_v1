# Import necessary libraries
import numpy as np
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize the Flask application
sales_revenue_forecaster_api = Flask("SuperKart Sales Revenue Forecaster")

# Load the trained machine learning model
model = joblib.load("sales_revenue_forecasting_model.joblib")

# Define a route for the home page (GET request)
@sales_revenue_forecaster_api.get('/')
def home():
    """
    This function handles GET requests to the root URL ('/') of the API.
    It returns a simple welcome message.
    """
    return "Welcome to the SuperKart Sales Revenue Forecaster API!"

# Define an endpoint for single property prediction (POST request)
@sales_revenue_forecaster_api.post('/v1/sales')
def forecast_sales_revenue_single(): # Renamed to avoid conflict with batch function
    """
    This function handles POST requests to the '/v1/sales' endpoint.
    It expects a JSON payload containing product details and returns
    the predicted sales revenue as a JSON response.
    """
    # Get the JSON data from the request body
    product_data = request.get_json()

    # Extract relevant features from the JSON data, matching the payload keys
    sample = {
        'Product_Weight': product_data['Product_Weight'],
        'Product_Sugar_Content': product_data['Product_Sugar_Content'],
        'Product_Allocated_Area': product_data['Product_Allocated_Area'],
        'Product_MRP': product_data['Product_MRP'],
        'Store_Size': product_data['Store_Size'],
        'Store_Location_City_Type': product_data['Store_Location_City_Type'],
        'Store_Type': product_data['Store_Type'],
        'Product_Id_char': product_data['Product_Id_char'],
        'Store_Age_Years': product_data['Store_Age_Years'],
        'Product_Type_Category': product_data['Product_Type_Category']
    }

    # Convert the extracted data into a Pandas DataFrame
    input_data = pd.DataFrame([sample])

    # Make log-transformed forecast
    forecasted_log_sales_revenue = model.predict(input_data)[0]

    # Inverse transform the log-transformed forecasting to get actual sales revenue
    forecasted_sales_revenue = np.expm1(forecasted_log_sales_revenue)

    # Convert forecasted_sales_revenue to Python float and round it
    forecasted_sales_revenue = round(float(forecasted_sales_revenue), 2)

    # Return the actual sales revenue
    return jsonify({'Forecasted Sales Revenue (in dollars)': forecasted_sales_revenue})


# Define an endpoint for batch forecasting (POST request)
@sales_revenue_forecaster_api.post('/v1/salesbatch')
def forecast_sales_revenue_batch(): # Renamed to avoid conflict with single forecasting function
    """
    This function handles POST requests to the '/v1/salesbatch' endpoint.
    It expects a CSV file containing product details for multiple products
    and returns the forecasted sales revenue as a dictionary in the JSON response.
    """
    # Get the uploaded CSV file from the request
    file = request.files['file']

    # Read the CSV file into a Pandas DataFrame
    input_data = pd.read_csv(file)

    # Make forecasts for all products in the DataFrame (get log_sales)
    # The model expects raw features as input, and the pipeline will handle preprocessing
    log_forecasts = model.forecast(input_data).tolist()

    # Calculate actual sales by inverse transforming the log predictions
    forecasted_sales = [round(float(np.expm1(log_sales)), 2) for log_sales in log_forecasts]

    # Create a dictionary of forecasts with product IDs as keys (assuming 'Product_Id' is in batch_data)
    # If 'Product_Id' is not present or dropped, you might need a different key or just return a list
    if 'Product_Id' in input_data.columns:
        product_ids = input_data['Product_Id'].tolist()
        output_dict = dict(zip(product_ids, forecasted_sales))
    else:
        output_dict = {'Forecasted Sales Revenue': forecasted_sales}

    # Return the forecasts dictionary as a JSON response
    return jsonify(output_dict)

# Run the Flask application in debug mode if this script is executed directly
if __name__ == '__main__':
    sales_revenue_forecaster_api.run(debug=True, host='0.0.0.0', port=7860)
