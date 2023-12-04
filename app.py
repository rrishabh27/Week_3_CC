import snowflake.connector
import pandas as pd
import streamlit as st
import plotly.express as px
import re
import os


# Set page configuration and background image
st.set_page_config(
    page_title="Book Insights",
    page_icon=":books:",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Streamlit code to display the dashboard
st.title('Book Data Dashboard :white :books:')


def set_bg_hack_url():
    '''
    A function to unpack an image from url and set as bg.
    Returns
    -------
    The background.
    '''
        
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url("https://cdn.pixabay.com/photo/2017/07/17/00/58/coffee-2511065_1280.jpg");
             background-size: cover
             background-color: #27f72a
         }}
         </style>
         """,
         unsafe_allow_html=True
     )
    
# st.markdown(
#     """
#     <style>
#     body {
#         background-color: #f0f0f0; /* Background color */
#         color: #333333; /* Text color */
#         font-size: 16px; /* Font size */
#     }
#     .css-1v7k31h, .st-bh, .st-ci {
#         color: #000000 !important; /* Dropdown menu, header, and plot text color */
#     }
#     .st-cq {
#         background-color: #ffffff; /* Widget background color */
#         border-radius: 10px;
#         padding: 20px;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )
    
    
set_bg_hack_url()



conn = snowflake.connector.connect(
    user=st.secrets['SNOWFLAKE_USER'],
    password=st.secrets['SNOWFLAKE_PASSWORD'],
    account=st.secrets['SNOWFLAKE_ACCOUNT'],
    database=st.secrets['SNOWFLAKE_DATABASE'],
    schema=st.secrets['SNOWFLAKE_SCHEMA']
)

# Query to retrieve book data from Snowflake
query = "SELECT * FROM BOOK_WEEK_3.KITAAB.BOOKS"
query_total_books = "SELECT COUNT(*) AS TOTAL_BOOKS FROM BOOKS"
query_best_category = (
    "SELECT CATEGORY, COUNT(*) AS BOOK_COUNT "
    "FROM BOOKS "
    "WHERE RATING = 'FIVE' "
    "GROUP BY CATEGORY "
    "LIMIT 1"
)
query_books_categories =  "SELECT DISTINCT CATEGORY FROM BOOKS"

# Function to fetch top 3 books for a selected category
def fetch_top_books_for_category(selected_category):
    # Snowflake query to fetch top 3 books in a selected category
    query_top_books_for_category = (
        f"SELECT CATEGORY, TITLE, RATING, PRICE, AVAILABILITY "
        f"FROM ( "
        f"   SELECT CATEGORY, TITLE, RATING, PRICE, AVAILABILITY, "
        f"       ROW_NUMBER() OVER (PARTITION BY CATEGORY ORDER BY RATING DESC) AS rank "
        f"   FROM BOOKS "
        f"   WHERE CATEGORY = '{selected_category}'"
        f") "
        f"WHERE rank <= 3"
    )

    # Snowflake connection and data retrieval
    conn = snowflake.connector.connect(
    user=st.secrets['SNOWFLAKE_USER'],
    password=st.secrets['SNOWFLAKE_PASSWORD'],
    account=st.secrets['SNOWFLAKE_ACCOUNT'],
    database=st.secrets['SNOWFLAKE_DATABASE'],
    schema=st.secrets['SNOWFLAKE_SCHEMA']
    )

    # Fetching data into a Pandas DataFrame directly from Snowflake
    top_books_for_category_df = pd.read_sql(query_top_books_for_category, conn)

    # Close Snowflake connection
    conn.close()

    return top_books_for_category_df



# Execute the query and fetch data into a Pandas DataFrame
df = pd.read_sql(query, conn)
# Fetching data into Pandas DataFrames directly from Snowflake
total_books_df = pd.read_sql(query_total_books, conn)
best_category_df = pd.read_sql(query_best_category, conn)
categories_df = pd.read_sql(query_books_categories, conn)

# Extracting values from DataFrames
total_books = total_books_df['TOTAL_BOOKS'][0] if not total_books_df.empty else 0


# Close Snowflake connection
conn.close()




# Display KPIs using Streamlit components
# st.title('Book Key Performance Indicators (KPIs)')

# Total number of books displayed using st.info

# col1 = st.columns(1)
st.metric("Total Number of Books", total_books)
# col2.metric("Total Number of Books", {total_books})

# st.subheader('Total Number of Books')
# st.info(f"Total Books: {total_books}")


# st.subheader('Top 3 Books in Each Category')
# Create a sidebar with a dropdown menu for selecting categories
with st.sidebar:
    selected_category = st.selectbox("Top 3 Books in Category:", categories_df['CATEGORY'])

    # Display top 3 books for the selected category in the main content area
    if selected_category:
        st.header(f'Top 3 Books in Category: {selected_category}')
        top_books_df = fetch_top_books_for_category(selected_category)
        st.dataframe(top_books_df[['TITLE', 'RATING', 'PRICE', 'AVAILABILITY']])




# Sorting options
sort_options = {
    'Title': 'TITLE',
    'Rating': 'RATING',
    'Price': 'PRICE'
}
selected_sort = st.selectbox('Sort by:', list(sort_options.keys()))

# Filtering options
availability_options = df['AVAILABILITY'].unique().tolist()
selected_availability = st.multiselect('Filter by Availability:', availability_options)

# Filter the DataFrame based on selected availability
filtered_df = df[df['AVAILABILITY'].isin(selected_availability)]


def extract_stock_count(availability):
    count = re.findall(r'\d+', availability)
    return int(count[0]) if count else 0

filtered_df = df[df['AVAILABILITY'].isin(selected_availability)]

# Function to convert string ratings to numeric values
def convert_rating_to_numeric(rating):
    rating_dict = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}  # Update based on your scale
    return rating_dict.get(rating.lower(), 0)

# Convert 'RATING' column to numeric
filtered_df = df[df['AVAILABILITY'].isin(selected_availability)]

# Function to extract numeric values from 'AVAILABILITY' column
def extract_stock_count(availability):
    count = re.findall(r'\d+', availability)
    return int(count[-1]) if count else 0

# Function to convert string ratings to numeric values
def convert_rating_to_numeric(rating):
    rating_dict = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}  # Update based on your scale
    return rating_dict.get(rating.lower(), 0)

# Apply function to create a new 'RATING_NUMERIC' column
filtered_df['RATING_NUMERIC'] = filtered_df['RATING'].apply(convert_rating_to_numeric)


# Apply function to create a new 'STOCK_COUNT' column
filtered_df['STOCK_COUNT'] = filtered_df['AVAILABILITY'].apply(extract_stock_count)

# Sort the DataFrame based on the selected sort option
sort_options_uppercase = {key.upper(): value for key, value in sort_options.items()}
sorted_df = filtered_df.sort_values(by=sort_options_uppercase[selected_sort.upper()])

# Display filtered and sorted data in a Streamlit table
st.write("Filtered and Sorted Book Data:")
st.dataframe(sorted_df)

# Visualization - Bar chart for average rating by availability
if not sorted_df.empty:
    avg_rating_by_availability = sorted_df.groupby('STOCK_COUNT')['RATING_NUMERIC'].mean().reset_index()
    fig = px.bar(avg_rating_by_availability, x='STOCK_COUNT', y='RATING_NUMERIC', 
                 title='Average Rating by Availability Count', labels={'STOCK_COUNT': 'Stock Count', 'RATING_NUMERIC': 'Average Rating'})
    st.plotly_chart(fig)
else:
    st.write("No data to display for visualization.")
    
    
## Genre Selection Dropdown
selected_genre = st.selectbox('Select a Genre:', filtered_df['CATEGORY'].unique(), 
                              format_func=lambda x: 'Choose a Genre' if x == '' else x)

# Filter data by selected genre
genre_filtered_df = filtered_df[filtered_df['CATEGORY'] == selected_genre]

# Display details about the selected genre
if not genre_filtered_df.empty and selected_genre != 'Choose a Genre':
    st.markdown(f"<h1 style='text-align: center; color: #333333;'>Details for {selected_genre} Category</h1>", 
                unsafe_allow_html=True)
    
    # Top Rated Books in the selected genre irrespective of availability
    st.subheader("Top Rated Books")
    top_rated_genre_books = genre_filtered_df.sort_values(by='RATING_NUMERIC', ascending=False).head(10)
    st.dataframe(top_rated_genre_books[['TITLE', 'RATING', 'PRICE']])
    
    # Average Price in the selected genre
    st.subheader("Average Price:")
    average_price_genre = genre_filtered_df['PRICE'].replace('[\£,]', '', regex=True).astype(float).mean()
    st.write(f"The average price in {selected_genre} category is £{average_price_genre:.2f}")
    
    # Other insights or visualizations specific to the selected genre can be added here
elif selected_genre == 'Choose a Genre':
    st.write("Please select a genre from the dropdown.")
else:
    st.write(f"No data available for {selected_genre} category.")