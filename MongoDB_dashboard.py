import streamlit as st
import pymongo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from collections import Counter

def read_keys_from_csv(file_path):
    """Read keys to consider from a CSV file.

    Parameters:
        file_path (str): Path to the CSV file containing keys to consider.

    Returns:
        list: A list of keys to consider.
    """
    df = pd.read_csv(file_path)
    return df['keys_to_consider'].tolist()

def calculate_professionals(data, keys_to_consider):
    """Calculate the total number of professionals (credits) for each year.

    Parameters:
        data (list): The data containing records for each year.
        keys_to_consider (list): The keys to consider for calculating professionals.

    Returns:
        Counter: A Counter object containing the total number of professionals for each year.
    """
    credits_counter = Counter()
    for record in data:
        if 'year' in record and isinstance(record['year'], int):
            year = record['year']
            credits_count = sum(len(record[key]) for key in keys_to_consider if key in record)
            credits_counter[year] += credits_count
        years = sorted(credits_counter.keys())
        credits = [credits_counter[year] for year in years]
    return credits

def calculate_seasons(data):
    year_counter = Counter()
    season_year_counter = Counter()

    # Count the occurrences of each year and each season
    for record in data:
        if 'year' in record and isinstance(record['year'], int):
            year = record['year']
            year_counter[year] += 1

            if 'number of seasons' in record and isinstance(record['number of seasons'], int):
                num_seasons = record['number of seasons']
            else:
                num_seasons = 1

            for y in range(year, year + num_seasons):
                season_year_counter[y] += 1

    years = sorted(set(year_counter.keys()).union(set(season_year_counter.keys())))
    original_frequencies = [year_counter.get(year, 0) for year in years]
    modified_frequencies = [season_year_counter.get(year, 0) for year in years]
    
    return years, original_frequencies, modified_frequencies

def export_data_to_csv(data, keys_to_consider):
    """
    Export the calculated data to a CSV file.
    
    The function fetches the data by calling other functions and generates a CSV file for download.
    
    Returns:
        None. The function generates a CSV file for download.
    """
    # Calculate the data using other functions in the script
    years, total_series, new_series = calculate_seasons(data)
    professionals = calculate_professionals(data, keys_to_consider)
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

def plot_data(data, plot_type, keys_to_consider):
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
    years, original_frequencies, modified_frequencies = calculate_seasons(data)
    
    # Call the existing `calculate_professionals` function
    credits = calculate_professionals(data, keys_to_consider)

    
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


def load_data_from_mongodb(connection_string, db_name, collection_name):
    """Load data from a MongoDB collection.

    Parameters:
        connection_string (str): The MongoDB connection string.
        db_name (str): The name of the database.
        collection_name (str): The name of the collection.

    Returns:
        list: The data loaded from the MongoDB collection.

    """
    client = pymongo.MongoClient(connection_string)
    db = client[db_name]
    collection = db[collection_name]
    data = list(collection.find({}))
    return data

def main():
    # Initialize session state
    if 'loaded_data' not in st.session_state:
        st.session_state.loaded_data = None
    # Create Streamlit interface
    st.title('MongoDB Data Analysis Dashboard')
    # Input fields for MongoDB connection
    connection_string = st.text_input('MongoDB Connection String:')
    db_name = st.text_input('Database Name:')
    collection_name = st.text_input('Collection Name:')
    keys_to_consider = read_keys_from_csv("./keys_to_consider.csv")
    # Load data when user presses the button
    if st.button('Load Data'):
        try:
            st.session_state.loaded_data = load_data_from_mongodb(connection_string, db_name, collection_name)
            st.write('Data successfully loaded!')
        except Exception as e:
            st.write('An error occurred:', e)
            st.session_state.loaded_data = None
    # Plot the data if it has been loaded
    if st.session_state.loaded_data:
        plot_type = st.selectbox('Select Plot Type', ['Bar Chart', 'Line Chart'])
        plot_data(st.session_state.loaded_data, plot_type, keys_to_consider)
    # Crea un pulsante Streamlit per l'esportazione dei dati
    if st.button('Esporta Dati in CSV'):
        csv = export_data_to_csv(st.session_state.loaded_data, keys_to_consider)
        # Crea un pulsante di download Streamlit per la stringa CSV
        st.download_button(
            label='Scarica Dati in CSV',
            data=csv,
            file_name='esportazione_dati.csv',
            mime='text/csv'
        )


if __name__ == '__main__':
    main()
