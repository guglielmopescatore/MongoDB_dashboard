import streamlit as st
import pymongo
import pandas as pd
import matplotlib.pyplot as plt
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
    return credits_counter

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

def plot_data(data, plot_type, keys_to_consider):
    # Call the `calculate_seasons` function to get the years and frequencies
    years, original_frequencies, modified_frequencies = calculate_seasons(data)
    
    # Call the existing `calculate_professionals` function
    credits_counter = calculate_professionals(data, keys_to_consider)

    # Create the first plot
    fig, ax = plt.subplots(figsize=(16, 8))

    if plot_type == 'Bar Chart':
        # Adjust the positions and width for the bars
        bar_width = 0.35
        index = range(len(years))

        # Create the bar charts
        ax.bar(index, original_frequencies, width=bar_width, label='Original Count', alpha=0.7)
        ax.bar([p + bar_width for p in index], modified_frequencies, width=bar_width, label='Modified Count (Seasons)',
               alpha=0.7)

        # Adjust the x-axis to fit the bar positions
        ax.set_xticks([p + bar_width / 2 for p in index])
        ax.set_xticklabels(years)
    else:
        ax.plot(years, original_frequencies, label='Original Count', marker='o')
        ax.plot(years, modified_frequencies, label='Modified Count (Seasons)', marker='x')

    ax.set_xlabel('Year')
    ax.set_ylabel('Series in Production')
    ax.legend()
    ax.set_title('Series in Production per Year')
    ax.grid(True)
    st.pyplot(fig)

    # Create the second plot
    fig, ax = plt.subplots(figsize=(16, 8))
    # plt.figure(figsize=(16, 8))
    years = sorted(credits_counter.keys())
    credits = [credits_counter[year] for year in years]
    if plot_type == 'Bar Chart':
        plt.bar(years, credits, label='Total Professionals')
    else:
        plt.plot(years, credits, label='Total Professionals')
    plt.xlabel('Year')
    plt.ylabel('Total Professionals')
    plt.title('Total Professionals per Year')
    plt.legend()
    plt.grid(True)
    st.pyplot(fig)

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
    

if __name__ == '__main__':
    main()
