import streamlit as st
from src.database import queries, utils, connection
import os
import plotly.express as px
# from dotenv import load_dotenv

#Load env vars from .env
# load_dotenv()

st.set_page_config(page_title = 'MySQL Data Viewer', layout="wide")

# Test database connection
# if not connection.test_connection():
#     st.error("Failed to connect to the database. Please check your .env file and database settings.")
#     st.stop()  # Stop the app if the connection fails

# Test the connection
if connection.test_mysql_connection():
    st.success("MySQL connection is working properly!")
    # Now you can proceed with your actual queries
#     df = conn.query('SELECT * from mytable;', ttl=600)
#     st.dataframe(df)
else:
    st.error("Failed to connect to MySQL database. Please check your connection settings.")



st.sidebar.success("Select a Page")


# Load Data
# Options for the dropdown menu
years = range(2019,  2025)
table_year = {year: f"vendite_list_{year}" for year in range(2019,  2026)}
# [f"vendite_list_{year}" for year in range(2019, 2026)]

# Create a selectbox in the sidebar
# selected_year = st.sidebar.selectbox(
#     "Select Year:",
#     table_year,
#     index=0,  # Default selection, None means no default
#     placeholder="Choose year",  # Placeholder text when no option is selected
# )

col1, col2 = st.columns([3,1], vertical_alignment = 'bottom', gap = 'medium')
with col1:

    selected_year = st.selectbox(
        "Select Year:",
        years,
        index=0,  # Default selection, None means no default
        placeholder="Choose year",  # Placeholder text when no option is selected
    )

with col2:

    button_load_data = st.button("Load Data")


@st.cache_data
def fetch_data(year, table_name):
   st.write("Run query: \n")
   qstr = queries.get_sales_table(table_name,  include_store=False)
   st.code(qstr, language='sql')
#    data = utils.validate_year(utils.execute_query(qstr),'year', year)
   data = utils.execute_query(qstr)
   return data

@st.cache_data
def fetch_data_wstore_info(year, table_name):
   st.write("Run query: \n")
   qstr = queries.get_sales_table(table_name)
   st.code(qstr, language='sql')
#    data = utils.validate_year(utils.execute_query(qstr),'year', year)
   data = utils.execute_query(qstr)
   return data

# Button to activate showing the schema
if button_load_data:
   if selected_year:  # Check if a table has been selected
   # Convert schema to DataFrame for easier display
      df_wstore = fetch_data_wstore_info(selected_year, f"vendite_list_{selected_year}")
      df_wtstore = utils.group_and_sum(df_wstore)
      df = fetch_data(selected_year, f"vendite_list_{selected_year}")
      total_revenue = df['monthly_total_sales'].sum()
      gross_profit = df['profit'].sum()
      gross_profit_margin = (gross_profit / total_revenue) * 100 if total_revenue else 0
      colns = st.columns(2)
      with colns[0]:
          st.write(df.dtypes)
          st.write(df)

      with colns[1]:
          st.write(df_wtstore.dtypes)
          st.write(df_wtstore)
#       st.write(utils.validate_year(df,'year',selected_year))

      col1, col2, col3 = st.columns(3)

      with col1:
          st.metric(label="总收入", value=f"${total_revenue:,.2f}", border=True)

      with col2:
          st.metric(label="利润", value=f"${gross_profit:,.2f}", border=True)

      with col3:
          st.metric(label="利润比例", value=f"{gross_profit_margin:.2f}%", border=True)

      df_piechart = utils.group_and_sum(df_wstore, group={3}, sum={-3})

      st.write(df_piechart)

      col1,col2 = st.columns(2)

      with col1:
# Create pie chart
          fig = px.pie(df_piechart, names='Negozio',
                       values='monthly_total_sales',
                       title='各个分店销售额度比例图',
          color_discrete_sequence=px.colors.sequential.RdBu)
# Update y-axis title
          st.plotly_chart(fig)

      with col2:
          # Create bar chart
          fig = px.bar(df_wtstore, x='month', y='monthly_total_sales',
                     title='柱状图',
                     height=400)
          fig.update_yaxes(title_text='月销售额')
          st.plotly_chart(fig)
# Display in Streamlit
   else:
      st.warning("Please select a table first.")

