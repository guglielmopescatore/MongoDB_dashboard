# MongoDB Data Analysis Dashboard

## Overview

This Streamlit application provides a user-friendly interface to visualize and analyze data from a MongoDB collection. Users can connect to a MongoDB database by providing the connection string, database name, and collection name. Once connected, the application offers two types of visualizations: Bar Charts and Line Charts, to understand the frequency of series produced per year and how the count changes when considering the number of seasons. The second chart display the number of crew members per year based on the data in the MongoDB collection. The application now reads from a `keys_to_consider.csv` file to determine which keys to consider for counting crew members. The dashboard provides an option for data export of the displayed graphs. By clicking the 'Export Data in CSV' button, users can download a .csv file containing the dataset relevant to the graphs for further analysis or reporting.

## Features

- **MongoDB Connection**: Securely connect to a MongoDB database.
- **Data Visualization**: View the data as either a Bar Chart or a Line Chart.
- **Interactive UI**: Interactive Graphs with Plotly
- **CSV export**: Data export of the displayed graphs

## Installation

### Requirements

- Python 3.x
- Streamlit
- Matplotlib
- Pandas
- Numpy
- Plotly
- pymongo
- dnspython

### Setting Up Your Environment

Create a new Python environment (Optional but recommended):

```bash
conda create --name your_env_name python=3.x
```

Activate the environment:

```bash
conda activate your_env_name
```

Install the required packages:

```bash
conda install -c conda-forge streamlit matplotlib panda nompy plotly pymongo dnspython
```
### External Files Required

#### keys_to_consider.csv
- This external file is required for the new crew members analysis feature.
- The file should contain the keys to consider for counting crew members.
- Place this file in the root directory of the project for the script to access it.

### Running the Application

To run the application, navigate to the directory where the `MongoDB_dashboard.py` file is located and run:

```bash
streamlit run MongoDB_dashboard.py
```

## Usage

1. Input the MongoDB connection string, database name, and collection name.
2. Click the "Load Data" button to fetch the data.
3. Choose the type of plot you want to see (Bar Chart or Line Chart) from the dropdown menu.
4. Click the "Export Data to CSV" button to export the data.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT License](https://choosealicense.com/licenses/mit/)

