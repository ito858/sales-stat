import streamlit as st
import time
from src.database import queries, utils, connection
import os
import pandas as pd
import plotly.express as px
from datetime import datetime

# 设置页面配置
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# 标题
st.title("Sales Analytics Dashboard")

# choose a connection_name from screte
connection_name = "database-1"
# Test the connection
if connection.test_mysql_connection(connection_name):
    st.success("MySQL connection is working properly!")
else:
    st.error("Failed to connect to MySQL database. Please check your connection settings.")


col_sale = 'Total_Sale'
col_cost = 'Total_Cost'
col_profit = 'Profit'
col_tax = 'Total_Tax'
# 加载数据
@st.cache_data
def get_data(year):
#    st.write("Run query: \n")
#    qstr = queries.get_sales_table(table_name,  include_store=False)
#         DAYOFMONTH(Data) AS Day,
   start_time = time.time()
   qstr = f"""
   SELECT
        YEAR(Data) AS Year,
        MONTH(Data) AS Month,
        ROUND(SUM(TotRighe), 2) AS {col_sale},
        ROUND(SUM(TotAcquisto), 2) AS {col_cost},
        ROUND(SUM(Guadagno), 2) AS {col_profit},
        ROUND(SUM(TotCodIva), 2) AS {col_tax},
        Negozio
    FROM vendite_list_{year}
    WHERE YEAR(Data) = {year}
    GROUP BY
        1,2, Negozio
    ORDER BY
        Year,
        Month;
    """
#    data = utils.validate_year(utils.execute_query(qstr),'year', year)
   st.code(qstr, language='sql')
   data = utils.execute_query(qstr, connection_name)
   end_time = time.time()
   exct_time = end_time - start_time
   st.success(f"Loading Data takes: {exct_time: .4f} seconds")
   return data

years = range(2019,  2020)
table_year = {year: f"vendite_list_{year}" for year in range(2019,  2020)}

# year_opt = store_filter = st.selectbox(
#     "Please Select Yeaer",
#     years,
#     index=None
#     )
# st.write("You have selected:", year_opt)
#
# # st.write("Click to load data, might take a few seconds")
# # button_load_data = st.button("Load Data")
#
#
c1 , c2 = st.columns(2, vertical_alignment = 'bottom', gap = 'medium')
with c1:
    year_opt = store_filter = st.selectbox(
        "Please Select Yeaer",
        years,
        index=None
        )

with c2:
#     st.write("Click to load data, might take a few seconds")
    button_load_data = st.button("Load Data")

st.write("You have selected:", year_opt)


#     if year_opt and button_load_data:
#     else:
#      st.write("You have not yet selected a year")

# 侧边栏 - 筛选器
# st.sidebar.header("Filters")
#
# if 'df' in locals():
#     category_filter = st.sidebar.multiselect(
#         "Select Category",
#         options=df['Categorie'].unique(),
#         default=df['Categorie'].unique()
#     store_filter = st.sidebar.multiselect(
#         "Select Store",
#         options=df['Negozio'].unique(),
#         default=df['Negozio'].unique()
#     )
#     )
# else:
#     st.sidebar.warning("Dataframe not loaded yet. Please load the data to use the filters.")

if button_load_data and year_opt:
 df = get_data(year_opt)
 st.write(df)
 if not df.empty:
  cols = st.columns(4)
  with cols[0]:
    total_revenue = df[col_sale].sum()
    st.metric(label="总收入", value=f"${total_revenue:,.2f}", border=True)

  with cols[1]:
    profit = df[col_cost].sum()
    total_cost = df[col_cost].sum()
    st.metric(label="总支出", value=f"${total_cost:,.2f}", border=True)

  with cols[2]:
    profit = df[col_profit].sum()
    st.metric(label="总利润", value=f"${profit:,.2f}", border=True)

  with cols[3]:
    tax = df[col_tax].sum()
    st.metric(label="税收", value=f"${tax:,.2f}", border=True)
 else:
    st.write('Load Data First')


 df_piechart = utils.group_and_sum(df, group={-1}, sum={3})
 df_linechart = utils.group_and_sum(df, group={1,2}, sum={3})
 col1,col2 = st.columns(2)
 with col1:
# Create pie chart
    fig1 = px.pie(df_piechart, names='Negozio',
               values=col_sale,
               title='各个分店销售额度比例图',
    color_discrete_sequence=px.colors.sequential.RdBu)
# Update y-axis title
    st.plotly_chart(fig1)
#
 with col2:
      # Create bar chart
     fig2 = px.bar(df_linechart, x='Month', y=col_sale,
                 title='柱状图',
                 height=400)
     fig2.update_yaxes(title_text='月销售额')
     st.plotly_chart(fig2)
