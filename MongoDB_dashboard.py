import streamlit as st
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, OperationFailure, InvalidURI
from pymongo import MongoClient
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from collections import Counter

@st.cache_resource
def get_collection(connection_string, db_name, collection_name):
    try:
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        client.server_info()  # Force a call to the server to verify that the connection is successfully established

        # Check if the database exists
        if db_name not in client.list_database_names():
            st.warning(f"The database '{db_name}' does not exist.")
            return None

        db = client[db_name]

        # Check if the collection exists
        if collection_name not in db.list_collection_names():
            st.warning(f"The collection '{collection_name}' does not exist.")
            return None

        collection = db[collection_name]
        return collection

    except InvalidURI:
        st.error("Invalid MongoDB URI. Please check the format.")
    except ConnectionFailure:
        st.error("Failed to connect to the server.")
    except ServerSelectionTimeoutError:
        st.error("Server selection timed out.")
    except OperationFailure:
        st.error("Operation failed.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

    return None
        
def read_keys_from_csv(file_path):
    """Read keys to consider from a CSV file.

    Parameters:
        file_path (str): Path to the CSV file containing keys to consider.

    Returns:
        list: A list of keys to consider.
    """
    df = pd.read_csv(file_path)
    return df['keys_to_consider'].tolist()

def export_data_to_csv(collection, keys_to_consider):
    """
    Export the calculated data to a CSV file.
    
    The function fetches the data by calling other functions and generates a CSV file for download.
    
    Returns:
        None. The function generates a CSV file for download.
    """
    # Calculate the data using other functions in the script
    years, total_series, new_series = calculate_seasons(collection)
    professionals = calculate_professionals(collection, keys_to_consider)
    # Trova la lunghezza massima tra le liste
    max_length = max(len(years), len(total_series), len(new_series), len(professionals))

    # Riempi le liste con NaN fino a raggiungere la lunghezza massima
    years = years + [np.nan] * (max_length - len(years))
    total_series = total_series + [np.nan] * (max_length - len(total_series))
    new_series = new_series + [np.nan] * (max_length - len(new_series))
    professionals = professionals + [np.nan] * (max_length - len(professionals))
    
    # Create a DataFrame from the calculated data
    df = pd.DataFrame({
        'Year': years,
        'Total Series in Production': total_series,
        'New Series': new_series,
        'Professionals': professionals
    })
    
    # Convert the DataFrame to a CSV string
    csv = df.to_csv(index=False)
    
    # Return the CSV string for further processing
    return csv

def plot_data(collection, plot_type, keys_to_consider):
    """
    Plot the given data using Plotly.
    
    Parameters:
    - data (DataFrame or dict): The data to be plotted.
    - plot_type (str): The type of plot to generate. Options are "Bar Chart" and "Line Chart".
    - keys_to_consider (list): The keys or columns in the data that should be considered for plotting.
    
    Returns:
    None. The function directly plots the graphs using st.plotly_chart().
    
    This function creates two plots:
    1. A comparison between 'Original Frequencies' and 'Modified Frequencies' over years.
    2. A distribution of 'Credits' over years.
    """
    # Call the `calculate_seasons` function to get the years and frequencies
    years, original_frequencies, modified_frequencies = calculate_seasons(collection)
    
    # Call the existing `calculate_professionals` function
    credits = calculate_professionals(collection, keys_to_consider)

    
    # Create the first plot using Plotly
    fig1 = go.Figure()

    if plot_type == 'Bar Chart':
        # Adding bars for original frequencies
        fig1.add_trace(go.Bar(x=years, y=original_frequencies, name='New Series'))
        # Adding bars for modified frequencies
        fig1.add_trace(go.Bar(x=years, y=modified_frequencies, name='Total Series in Production'))
    else:
        # Adding line for original frequencies
        fig1.add_trace(go.Scatter(x=years, y=original_frequencies, mode='lines+markers', name='New Series'))
        # Adding line for modified frequencies
        fig1.add_trace(go.Scatter(x=years, y=modified_frequencies, mode='lines+markers', name='Total Series in Production'))

    # Additional layout settings
    
    # Update colors and layout for the first figure
    fig1.update_traces(marker=dict(color='rgba(135, 206, 250, 0.8)'), selector=dict(name='New Series'))
    fig1.update_traces(marker=dict(color='rgba(255, 87, 34, 0.8)'), selector=dict(name='Total Series in Production'))
    fig1.update_layout(
        title='Series in Production per Year',
        xaxis_title='Years',
        yaxis_title='Series',
    )
    
    # Show the first figure
    st.plotly_chart(fig1)
# Create the second plot
    
    # Create the second plot using Plotly
    fig2 = go.Figure()
    #years = sorted(credits_counter.keys())
    #credits = [credits_counter[year] for year in years]
    if plot_type == 'Bar Chart':
        # Adding bars for credits
        fig2.add_trace(go.Bar(x=years, y=credits, name='Professionals'))
    else:
        # Adding line for credits
        fig2.add_trace(go.Scatter(x=years, y=credits , mode='lines+markers', name='Professionals'))
    # Update colors and layout for the second figure
    fig2.update_traces(marker=dict(color='rgba(50, 171, 96, 0.7)'), selector=dict(name='Professionals'))
    # Additional layout settings
    fig2.update_layout(
        title='Total Professionals per Year',
        xaxis_title='Years',
        yaxis_title='Professionals',
    )
    
    # Show the second figure
    st.plotly_chart(fig2)


def calculate_professionals(collection, keys_to_consider):
    """Calculate the total number of professionals (credits) for each year using MongoDB queries.

    Parameters:
        collection (str): Collection name.
        keys_to_consider (list): The keys to consider for calculating professionals.

    Returns:
        Counter: A Counter object containing the total number of professionals for each year.
    """
    
    # Select collection
    collection = collection

    # Initialize counter
    credits_counter = Counter()

    # Create the aggregation pipeline
    sum_fields = {}
    for key in keys_to_consider:
        sum_fields[key] = {
            "$cond": {
                "if": {"$isArray": f"${key}"},
                "then": {"$size": f"${key}"},
                "else": 0
            }
    }
    pipeline = [
        {"$group": {
            "_id": "$year",
            "total_credits": {"$sum": {"$add": list(sum_fields.values())}}
        }},
        {"$sort": {"_id": 1}}  # Sort by year
    ]

    # Run the aggregation
    aggregation_result = collection.aggregate(pipeline)

    # Populate the counter with the results
    for record in aggregation_result:
        if record["_id"] is not None:
            credits_counter[record["_id"]] = record["total_credits"]
    years = sorted(credits_counter.keys())
    credits = [credits_counter[year] for year in years]
    return credits



def calculate_seasons(collection):
    """
    Calculate the number of products and seasons per year directly using MongoDB queries.
    This version uses Counters to store frequencies and also returns lists suitable for plotting.

    Parameters:
        collection (str): Collection name.

    Returns:
        years (list): List of years.
        original_frequencies_list (list): List of the number of products per year.
        modified_frequencies_list (list): List of the number of seasons per year.
    """

    # Select collection

    collection = collection
    
    # Counters to store the results
    original_frequencies = Counter()
    modified_frequencies = Counter()
    
    # Use aggregation framework to count the number of products per year
    pipeline_products = [
        {"$match": {"year": {"$ne": None}}},
        {"$group": {"_id": "$year", "count": {"$sum": 1}}}
    ]

    aggregated_result_products = list(collection.aggregate(pipeline_products))
    
    for item in aggregated_result_products:
        original_frequencies[item['_id']] = item['count']
    
    # Custom logic for calculating seasons per year
    pipeline_seasons = [
        {"$match": {"year": {"$ne": None}}},  # Exclude nulls for 'year'
        {"$project": {
            "year": 1,
            "number of seasons": {
                "$cond": [
                    {"$or": [
                        {"$eq": [{"$type": "$number of seasons"}, "null"]},
                        {"$ne": [{"$type": "$number of seasons"}, "int"]}
                    ]},
                    1,
                    "$number of seasons"
                ]
            }
        }},
        {"$addFields": {  # Logging intermediate result
            "end_range": {"$add": ["$year", "$number of seasons"]}
        }},
        {"$project": {
            "year_range": {
                "$cond": [
                    {"$eq": ["$end_range", None]},
                    {"end_range": {"$add": ["$year", 1]}},
                    {"$range": ["$year", "$end_range"]}
                ]
            }
        }},
        {"$unwind": {"path": "$year_range"}},
        {"$group": {"_id": "$year_range", "count": {"$sum": 1}}}
    ]

    aggregated_result_seasons = list(collection.aggregate(pipeline_seasons))
    
    for item in aggregated_result_seasons:
        modified_frequencies[item['_id']] = item['count']
    
    # Sorting the lists based on years for better readability and further processing
    years = sorted(set(original_frequencies.keys()).union(set(modified_frequencies.keys())))
    
    # Convert Counters to lists for plotting
    original_frequencies_list = [original_frequencies.get(year, 0) for year in years]
    modified_frequencies_list = [modified_frequencies.get(year, 0) for year in years]
    
    return years, original_frequencies_list, modified_frequencies_list

def main():
    # Initialize session state
    if 'collection' not in st.session_state:
        st.session_state.collection = None
    st.title('MongoDB Data Analysis Dashboard')
    # Input fields for MongoDB connection
    connection_string = st.text_input('MongoDB Connection String:')
    db_name = st.text_input('Database Name:')
    collection_name = st.text_input('Collection Name:')
    keys_to_consider = read_keys_from_csv("./keys_to_consider.csv")
   
    # Ploat data when user presses the button
    if st.button('Plot Data'):
        st.session_state.collection = get_collection(connection_string, db_name, collection_name)
        if st.session_state.collection is not None:
            st.success("Connessione stabilita.")
        else:
            st.warning("Connessione non stabilita. Verifica gli errori.")
    if st.session_state.collection is not None:
        plot_type = st.selectbox('Select Plot Type', ['Bar Chart', 'Line Chart'])
        plot_data(st.session_state.collection, plot_type, keys_to_consider)
        # Creates a Streamlit button for exporting data
    if st.button('Export Data to CSV'):
        csv = export_data_to_csv(collection, keys_to_consider)
        # Create a Streamlit download button for the CSV file
        st.download_button(
            label='Download Data to CSV',
            data=csv,
            file_name='esportazione_dati.csv',
            mime='text/csv'
        )


if __name__ == '__main__':
    main()
