import pandas as pd


def load_coral_data(file_path):
    """
    Load coral data from a CSV file.

    Parameters:
    file_path (str): The path to the CSV file containing coral data.

    Returns:
    pd.DataFrame: A DataFrame containing the loaded coral data.
    """
    try:
        coral_data = pd.read_csv(file_path, sep=';')
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


if __name__ == "__main__":
    # Example usage
    file_path = "data/202603_GFASC_FEF_Settlement_Assays.csv"
    print(f"Loading coral data from: {file_path}")
    coral_data = load_coral_data(file_path)
    print_info_loaded_data(coral_data)
