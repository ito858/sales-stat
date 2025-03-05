import streamlit as st
# import mysql.connector
# from dotenv import load_dotenv
# import os

# Load environment variables from .env file
# load_dotenv()

def get_connection(name = "my_sql_connection"):
    try:
        # Init the connection
        # conn = st.connection('mysql', type='sql')
        conn = st.connection(
            name , type="streamlit.connections.SQLConnection"
        )
        # connection = mysql.connector.connect(
        #     host=os.getenv("DB_HOST"),
        #     database=os.getenv("DB_NAME"),
        #     user=os.getenv("DB_USER"),
        #     password=os.getenv("DB_PASSWORD")
        # )
        return conn
    except Exception as err:  # Added Exception type and fixed indentation
        print(f"Error connecting to database: {err}")
        return None


def test_mysql_connection(name):
    """
    Test if the MySQL connection is working properly.

    Args:
        connection: The Streamlit MySQL connection object

    Returns:
        bool: True if connection works, False otherwise
    """
    try:
        # Try a simple query that should work on any MySQL database
        connection= get_connection(name)
        result = connection.query("SELECT 1")
        # If we got a result with the value 1, connection works
        return not result.empty and result.iloc[0, 0] == 1
    except Exception as e:
        print(f"Connection test failed: {str(e)}")
        return False


# def test_connection():
#     """Tests the database connection and returns True if successful, False otherwise."""
#     connection = get_connection()
#     if connection:
#         print("Connection to database successful!")
#         connection.close()  # Close the connection after testing
#         return True
#     else:
#         print("Failed to connect to database.")
#         return False
