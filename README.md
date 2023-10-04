# MongoDB Data Analysis Dashboard

## Overview

This Streamlit application provides a user-friendly interface to visualize and analyze data from a MongoDB collection. Users can connect to a MongoDB database by providing the connection string, database name, and collection name. Once connected, the application offers two types of visualizations: Bar Charts and Line Charts, to understand the frequency of series produced per year and how the count changes when considering the number of seasons.

## Features

- **MongoDB Connection**: Securely connect to a MongoDB database.
- **Data Visualization**: View the data as either a Bar Chart or a Line Chart.
- **Interactive UI**: Easily switch between different types of visualizations.

## Installation

### Requirements

- Python 3.x
- Streamlit
- Matplotlib
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
conda install -c conda-forge streamlit matplotlib pymongo dnspython
```

### Running the Application

To run the application, navigate to the directory where the `MongoDB_dashboard.py` file is located and run:

```bash
streamlit run MongoDB_dashboard.py
```

## Usage

1. Input the MongoDB connection string, database name, and collection name.
2. Click the "Load Data" button to fetch the data.
3. Choose the type of plot you want to see (Bar Chart or Line Chart) from the dropdown menu.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT License](https://choosealicense.com/licenses/mit/)
