import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import config


def load_coral_data(file_path):
    """
    Load coral data from a CSV file.

    Parameters:
    file_path (str): The path to the CSV file containing coral data.

    Returns:
    pd.DataFrame: A DataFrame containing the loaded coral data.
    """
    try:
        coral_data = pd.read_csv(file_path, sep=";")
        return coral_data

    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return None
    except pd.errors.EmptyDataError:
        print("Error: The file is empty.")
        return None
    except pd.errors.ParserError:
        print("Error: There was a parsing error while reading the file.")
        return None


def print_info_loaded_data(dataframe):
    """
    Print information about the loaded coral data.

    Parameters:
    dataframe (pd.DataFrame): The DataFrame containing the loaded data
    """
    if dataframe is not None:
        print(f"First 5 rows: \n{dataframe.head(5)}")
        print(f"{dataframe.shape[0]} rows and {dataframe.shape[1]} columns loaded successfully.")
        print("Table info:")
        dataframe.info()
        print(f"Column names: {dataframe.columns.tolist()}")
    else:
        print("No data to display. Please check the file path and ensure the file is not empty or corrupted.")


def data_preparation(dataframe, behavior_columns, total_larvae_column="TOTAL_LARVAE_SET"):
    """
    Prepare the coral data for analysis.

    Parameters:
    dataframe (pd.DataFrame): The DataFrame containing the loaded data
    behavior_columns (list): List of column names for behavior data
    total_larvae_column (str): Name of the column containing the total number of larvae in the replicate

    What it does:
    Add a NB_DEAD column containing the number of dead larvae in the batch.
    Remove the rows where NB_DEAD < 0

    Returns:
    The updated dataframe
    """
    if dataframe is not None:
        settled_larvae = dataframe[behavior_columns].sum(axis=1)
        dataframe["NB_DEAD"] = dataframe[total_larvae_column] - settled_larvae

        negative_dead_mask = dataframe["NB_DEAD"] < 0
        if negative_dead_mask.any():
            print("---- WARNING - Negative dead values ----")
            print(f"rows with negative dead values:\n{dataframe[negative_dead_mask]}")
            dataframe = dataframe.drop(dataframe[negative_dead_mask].index)
            print("---- These rows have been removed ----\n")
        return dataframe

    else:
        print("No data to prepare. Please check the file path and ensure the file is not empty or corrupted.")
        return None


def compute_percentage(dataframe, count_columns, total, info_columns):
    """
    Compute percentages

    Arguments:
    dataframe (pd.DataFrame): The DataFrame containing the loaded data
    count_columns (list): Columns on which to compute the percentage
    total (pd.Series): Reference column to compute the percentage
    info_columns (list): columns with important info to keep

    What it does:
    Compute percentage for each columns
    Sanity check: check if the sum of all columns is equal to 100.

    Returns:
    A Dataframe with the percentage and the info columns
    """
    percentage = dataframe[count_columns].div(total, axis=0) * 100
    # Sanity check
    sum_percentage = percentage[count_columns].sum(axis=1)
    wrong_sum_mask = ~np.isclose(sum_percentage, 100) # ~ inverts the mask (True becomes False, as we want the false rows)
    if wrong_sum_mask.any():
        print("---- WARNING - Some percentage sum different from 100 ----")
        print(f"rows with weird percentage:\n{dataframe[wrong_sum_mask]}")

    result = pd.concat([dataframe[info_columns], percentage], axis=1)

    return result


if __name__ == "__main__":

    file_path = config.FILE_PATH
    print(f"Loading coral data from: {file_path}")
    coral_data = load_coral_data(file_path)
    print_info_loaded_data(coral_data)

    info_columns = config.INFO_COLUMNS
    behavior_columns = config.BEHAVIOR_COLUMNS

    coral_data = data_preparation(coral_data, behavior_columns)
    behavior_columns = behavior_columns + ["NB_DEAD"]

    columns_to_display = info_columns + behavior_columns
    print(coral_data[columns_to_display].head(5))

    percentage = compute_percentage(coral_data,
                                    behavior_columns,
                                    coral_data[config.TOTAL_LARVAE_REPLICATE],
                                    info_columns)
    print(percentage.head(5))
    