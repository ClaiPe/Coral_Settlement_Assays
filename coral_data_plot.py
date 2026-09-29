import pandas as pd
import matplotlib.pyplot as plt


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

        negative_dead_rows = dataframe[dataframe["NB_DEAD"] < 0]
        if any(negative_dead_rows):
            print("---- WARNING - Negative dead values ----")
            print(f"rows with negative dead values:\n{negative_dead_rows}")
            dataframe = dataframe.drop(negative_dead_rows.index)
            print("---- These rows have been removed ----\n")
        return dataframe

    else:
        print("No data to prepare. Please check the file path and ensure the file is not empty or corrupted.")
        return None


if __name__ == "__main__":
    file_path = "data/202603_GFASC_FEF_Settlement_Assays.csv"
    print(f"Loading coral data from: {file_path}")
    coral_data = load_coral_data(file_path)
    print_info_loaded_data(coral_data)

    mean_settlers_by_treatment = coral_data.groupby("TREATMENT")["PERCENTAGE_SETTLERS"].mean()
    print(f"Mean settlement by treatment:\n{mean_settlers_by_treatment}")

    info_columns = ["COHORT_ID", "TREATMENT", "AGE_LARVAE"]
    behavior_columns = ["NB_CCA_SETTLERS_TOP",
                        "NB_CCA_SETTLERS_BOTTOM",
                        "NB_PETRIDISH_SETTLERS",
                        "NB_HANGERS",
                        "NB_SWIMMING",
                        "NB_NOT_SWIMMING",
                        "NB_CAULIFLOWERS"]

    columns_to_display = info_columns + behavior_columns
    print(coral_data[columns_to_display].head(5))

    coral_data = data_preparation(coral_data, behavior_columns)
    print(coral_data.head())