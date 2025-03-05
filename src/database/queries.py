from pydantic import BaseModel, validator
from typing import List, Dict, Any

def get_all_customers():
    """Returns an SQL query to retrieve all customers."""
    return "SELECT * FROM customers;"

def get_customer_by_id(customer_id):
    """Returns an SQL query to retrieve a customer by ID."""
    return f"SELECT * FROM customers WHERE customer_id = {customer_id};"

def get_table_by_name(table_name):
    return f"DESC {table_name};"

def get_sales_table(table_name, store_id):
    query = f"""
    SELECT
        YEAR(Data) AS year,
        MONTH(Data) AS month,
        ROUND(SUM(TotRighe), 2) AS monthly_total_sales,
        ROUND(SUM(TotAcquisto), 2) AS monthly_total_cost,
        ROUND(SUM(TotRighe) - SUM(TotAcquisto), 2)  AS profit
    FROM
        {table_name}
    WHERE
        Negozio = {store_id}
    GROUP BY
        YEAR(Data),
        MONTH(Data)
    ORDER BY
        year,
        month;
    """
    return query


# def get_sales_table(table_name):
#     query = f"""
#     SELECT
#         YEAR(Data) AS year,
#         MONTH(Data) AS month,
#         ROUND(SUM(TotRighe), 2) AS monthly_total_sales,
#         ROUND(SUM(TotAcquisto), 2) AS monthly_total_cost,
#         ROUND(SUM(TotRighe) - SUM(TotAcquisto), 2)  AS profit
#     FROM
#         {table_name}
#     GROUP BY
#         YEAR(Data),
#         MONTH(Data)
#     ORDER BY
#         year,
#         month;
#     """
#     return query

def get_sales_table(table_name: str, include_store: bool = True) -> str:
    """
    Generate a MySQL query for sales data, with an option to include or exclude the Negozio column.

    Args:
        table_name (str): The name of the table to query.
        include_store (bool): Whether to include the Negozio (store) column in the query. Defaults to True.

    Returns:
        str: The generated MySQL query.
    """
    # Base SELECT clause components
    select_fields = [
        "YEAR(Data) AS year",
        "MONTH(Data) AS month",
        "ROUND(SUM(TotRighe), 2) AS monthly_total_sales",
        "ROUND(SUM(TotAcquisto), 2) AS monthly_total_cost",
        "ROUND(SUM(TotRighe) - SUM(TotAcquisto), 2) AS profit"
    ]

    # Add Negozio if requested
    if include_store:
        select_fields.insert(2, "Negozio")

    # Build the query
    query = (
        "SELECT\n"
        "    " + ",\n    ".join(select_fields) + "\n"
        "FROM\n"
        f"    {table_name}\n"
        "GROUP BY\n"
        f"    YEAR(Data),\n"
        f"    MONTH(Data)" + (",\n    Negozio" if include_store else "") + "\n"
        "ORDER BY\n"
        "    year,\n"
        "    month;"
    )

    return query


class QueryParameters(BaseModel):
    """
    A Pydantic model to encapsulate the parameters for generating the SQL query.
    Uses automatic type validation and error handling.
    """
    sum_columns: List[str]
    non_sum_columns: List[str]
    table_name: str
    year: int
    alias_map: Dict[str, str]

    @validator("year")
    def year_must_be_positive(cls, year):
        if year <= 0:
            raise ValueError("Year must be a positive integer.")
        return year


def generate_sql_query(params: QueryParameters) -> str:
    """
    Generates a SQL query to aggregate data based on the provided parameters.

    Args:
        params: An instance of the QueryParameters Pydantic model.

    Returns:
        A string containing the generated SQL query.
    """

    # Build the SELECT clause
    select_clause = "SELECT\n"
    select_clause += "     YEAR(Data) AS Year,\n"
    select_clause += "     MONTH(Data) AS Month,\n"

    for column in params.sum_columns:
        if column in params.alias_map:  # Only include if alias is provided
            alias = params.alias_map[column]
            select_clause += f"     ROUND(SUM({column}), 2) AS {alias},\n"
        else:
            print(f"Warning: Column '{column}' is in sum_columns but not in alias_map.  It will be skipped in the SELECT statement.")

    # Add non-sum columns to select clause
    for column in params.non_sum_columns:
        select_clause += f"     {column},\n"

    # Remove the trailing comma and newline
    select_clause = select_clause.rstrip(',\n')

    # Build the FROM clause
    from_clause = f"\n FROM {params.table_name}"

    # Build the WHERE clause
    where_clause = f"\n WHERE YEAR(Data) = {params.year}"

    # Build the GROUP BY clause
    group_by_clause = "\n GROUP BY\n"
    group_by_fields = ["1", "2"] + [col for i, col in enumerate(params.non_sum_columns)]
    group_by_clause += "     " + ", ".join(group_by_fields)

    # Build the ORDER BY clause
    order_by_clause = "\n ORDER BY\n"
    order_by_clause += "     Year,\n"
    order_by_clause += "     Month"

    # Combine all clauses
    sql_query = select_clause + from_clause + where_clause + group_by_clause + order_by_clause + ";"

    return sql_query

