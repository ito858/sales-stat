import streamlit as st
from src.database import queries, utils, connection


def fetch_kpi_table():
    if selected_year and selected_store:  # Check if a table has been selected
        st.write("Run query: \n")
        st.write(queries.get_sales_table(selected_year, selected_store))
        data = utils.execute_query(queries.get_sales_table(selected_year, selected_store))
        # Convert schema to DataFrame for easier display
        st.write(f"Sales data fetched")
    else:
        st.warning("Please select a table first.")
    return data


# Options for the dropdown menu
table_year = [f"vendite_list_{year}" for year in range(2019, 2026)]

# Create a selectbox in the sidebar
selected_year = st.sidebar.selectbox(
    "Select Year:",
    table_year,
    index=0,  # Default selection, None means no default
    placeholder="Choose year",  # Placeholder text when no option is selected
)

# Function to fetch distinct store IDs

def get_store_ids(table_name):
    query = f"SELECT DISTINCT Negozio FROM {table_name}"
    result = utils.execute_query(query)
    st.write("Query Result:", result)  # Debugging: print the result
    return result['Negozio'].tolist()

# Fetch store IDs for the selected year
store_ids = get_store_ids(selected_year)

# Create a selectbox in the sidebar for store IDs
selected_store = st.sidebar.selectbox(
    "Select Store ID:",
    store_ids,
    index=0,  # Default selection
    placeholder="Choose store ID",  # Placeholder text when no option is selected
)

# Display the selected options
st.write("You selected year:", selected_year)
st.write("You selected store:", selected_store)

# Button to activate showing the schema
if st.button("Show Sales Table"):
    data = fetch_kpi_table()
    total_revenue = data['monthly_total_sales'].sum()
    gross_profit = data['profit'].sum()
    gross_profit_margin = (gross_profit / total_revenue) * 100 if total_revenue else 0
    # Convert schema to DataFrame for easier display
    st.write(f"Sales Table")
    st.table(data)

# Display KPIs in the top row
    col1, col2, col3 = st.columns((2,2,1))

    with col1:
        st.metric(label="Total Revenue", value=f"${total_revenue:,.2f}")

    with col2:
        st.metric(label="Gross Profit", value=f"${gross_profit:,.2f}")

    with col3:
        st.metric(label="Gross Profit Margin", value=f"{gross_profit_margin:.2f}%")


if st.button("Show Bar Chart"):
   df = fetch_kpi_table()

   st.bar_chart(df, x="month", y="monthly_total_sales")

# Example usage:
# if data is not None:
#     st.write("Sales Table:")
#     st.dataframe(data)
# else:
#     st.error("Failed to retrieve customer data. Ensure database is running and credentials are correct.")



