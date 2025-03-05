from pydantic import BaseModel, validator
from typing import List, Dict, Any
import streamlit as st

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


# Example Usage:
try:
    params = QueryParameters(
        sum_columns=["TotRighe", "TotAcquisto", "Guadagno", "TotCodIva"],
        non_sum_columns=["Negozio"],
        table_name="vendite_list_2023",
        year=2023,
        alias_map={
            "TotRighe": "Total_Sales",
            "TotAcquisto": "Total_Cost",
            "Guadagno": "Profit"
            # "TotCodIva" is intentionally missing from the alias_map
        }
    )

    sql_query = generate_sql_query(params)
    st.code(sql_query, language='sql')

except ValueError as e:
    print(f"Error: {e}")

except Exception as e:
  print(f"An unexpected error occurred: {e}")
