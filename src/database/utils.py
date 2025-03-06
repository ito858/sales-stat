import pandas as pd
from .connection import get_connection

def execute_query(query, connection_name):
    connection = get_connection(connection_name)
    if connection:
        try:
#             df = pd.read_sql(query, connection)
            df = connection.query(query, ttl=3600)
            return df
        except Exception as e:
            print(f"Error executing query: {e}")
            return None
    else:
        return None



def group_and_sum(df, group={1,2}, sum={-3,-2,-1}):
    """
    Group DataFrame by specified column positions and sum specified column positions
    using 1-based indexing (1 is first column, -1 is last column)

    Parameters:
    df (pd.DataFrame): Input DataFrame
    group (set): Set of column positions to group by (1-based, positive/negative)
    sum (set): Set of column positions to sum (1-based, positive/negative)

    Returns:
    pd.DataFrame: Grouped and summed result
    """
    # Validate inputs
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    if not isinstance(group, set) or not isinstance(sum, set):
        raise ValueError("group and sum must be sets")

    total_cols = len(df.columns)

    # Convert 1-based indices to 0-based for pandas
    def convert_index(idx, total):
        if idx > 0:
            if idx > total:
                raise ValueError(f"Column index {idx} exceeds number of columns {total}")
            return idx - 1
        elif idx < 0:
            if abs(idx) > total:
                raise ValueError(f"Column index {idx} exceeds number of columns {total}")
            return total + idx
        raise ValueError("Column indices must be non-zero")

    # Convert group and sum indices
    try:
        group_cols = [df.columns[convert_index(i, total_cols)] for i in sorted(group)]
        sum_cols = [df.columns[convert_index(i, total_cols)] for i in sorted(sum)]
    except IndexError:
        raise ValueError("Invalid column index provided")

    # Check for overlap
    if set(group_cols) & set(sum_cols):
        raise ValueError("Group and sum columns cannot overlap")

    # Create copy and perform operation
    df_copy = df.copy()
    result = df_copy.groupby(group_cols)[sum_cols].sum().reset_index()

    return result

def validate_year(df, column_name, year : str):
    # Filter the DataFrame to only include rows where the year matches the given year
    filtered_df = df[df[column_name] == int(year)]
    return filtered_df
