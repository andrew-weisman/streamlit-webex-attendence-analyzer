"""
Attendance Visualization Module

This module provides functionality to visualize session attendance data using Streamlit and Plotly.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# Function to load data from a CSV or Excel file
@st.cache_data
def load_data(file_path):
    """
    Load data from a CSV or Excel file.

    Parameters:
    file_path (str): The path to the data file.

    Returns:
    pd.DataFrame: The loaded data.
    """
    try:
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            return pd.read_excel(file_path)
        else:
            st.error("Unsupported file format")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Function to list all data files in the 'datafiles' directory
def list_data_files():
    """
    List all CSV and Excel files in the 'datafiles' directory.

    Returns:
    list: A list of filenames.
    """
    return [f for f in os.listdir('datafiles') if f.endswith('.csv') or f.endswith('.xlsx')]

def main():
    """
    Main function to visualize session attendance using Streamlit and Plotly.

    This function performs the following steps:
    1. Displays a Streamlit title and a widget to select a data file.
    2. Loads the selected data file.
    3. Processes the data to convert join and leave times to datetime objects.
    4. Sorts the data by "Display Name" case-insensitively.
    5. Groups the data by "Attendee Email".
    6. Creates a Plotly figure to visualize attendance over time.
    7. Adds traces to the figure for each attendee, showing their presence over time.
    8. Configures the layout of the figure and displays it using Streamlit.

    Note:
    - The data file should be located in the 'datafiles' directory.
    - The data should contain columns 'Join Time', 'Leave Time', 'Display Name', 'Attendee Email', 'Meeting Start Time', and 'Meeting End Time'.

    Returns:
    None
    """

    # Streamlit widget to select a data file
    st.title('Session Attendance Visualization')
    data_files = list_data_files()
    selected_file = st.selectbox("Choose a data file", data_files)

    # Check if any file is selected
    if not selected_file:
        st.warning("No data files found in the 'datafiles' directory. Please upload a data file.")
        return

    # Load the selected data file
    file_path = os.path.join('datafiles', selected_file)
    data = load_data(file_path)

    # Check if data is loaded successfully
    if data.empty:
        st.error("No data available to visualize.")
        return

    # Process the data: Convert join and leave times to datetime objects
    data['Join Time'] = pd.to_datetime(data['Join Time'].str.replace('="', '').str.replace('"', ''))
    data['Leave Time'] = pd.to_datetime(data['Leave Time'].str.replace('="', '').str.replace('"', ''))

    # Sort the data by "Display Name" case-insensitively
    data = data.sort_values(by='Display Name', key=lambda x: x.str.lower())

    # Group the data by "Attendee Email"
    grouped = data.groupby('Attendee Email')

    # Create a Plotly figure
    fig = go.Figure()

    # Use uniform spacing for y-axis values
    y_spacing = 1.0 / (len(grouped) + 1)
    y_value = 1.0 - y_spacing  # Start from the top

    # Iterate over groups in sorted order by "Display Name"
    for display_name in data['Display Name'].unique():
        group = data[data['Display Name'] == display_name]
        email = group['Attendee Email'].iloc[0]

        times = []
        presence = []
        hover_text = []

        # Add join and leave times for each attendee
        for _, row in group.iterrows():
            times.extend([row['Join Time'], row['Leave Time'], None])
            presence.extend([y_value, y_value, None])
            hover_text.extend([f'{display_name} ({email})', f'{display_name} ({email})', None])

        # Add a trace for each attendee
        fig.add_trace(go.Scatter(
            x=times,
            y=presence,
            mode='lines+markers',
            name=f'{display_name} ({email})',
            hoverinfo='text',
            text=hover_text
        ))

        y_value -= y_spacing  # Move down for the next line

    # Add "Not present" line
    session_start = data['Meeting Start Time'].iloc[0]
    session_end = data['Meeting End Time'].iloc[0]
    session_start = pd.to_datetime(session_start.replace('="', '').replace('"', ''))
    session_end = pd.to_datetime(session_end.replace('="', '').replace('"', ''))

    # Configure the layout of the figure
    fig.update_layout(
        title='Attendance Over Time',
        xaxis_title='Time',
        yaxis_title='Presence',
        yaxis=dict(
            tickvals=[],
            ticktext=[]
        ),
        hovermode='closest'
    )

    # Display the figure using Streamlit
    st.plotly_chart(fig)

# Run the main function
if __name__ == '__main__':
    main()
