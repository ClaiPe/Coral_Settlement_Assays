from pathlib import Path

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


def percentage_sanity_check(dataframe, count_columns):
    """
    Test to check if the sum of percentages is equal to 100.

    Arguments:
    dataframe (pd.DataFrame): dataframe containing the percentages to check
    count_columns (list): list of columns containing the percentages

    Returns:
    Nothing if no weird percentage.
    If weird percentage, returns the problematic rows.
    """
    sum_percentage = dataframe[count_columns].sum(axis=1)
    wrong_sum_mask = ~np.isclose(sum_percentage, 100) # ~ inverts the mask (True becomes False, as we want the false rows)
    if wrong_sum_mask.any():
        print("---- WARNING - Some percentage sum different from 100 ----")
        print(f"rows with weird percentage:\n{dataframe[wrong_sum_mask]}")


def compute_percentage_per_row(dataframe, count_columns, total, info_columns):
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
    percentage = dataframe[count_columns].div(dataframe[total], axis=0) * 100
    percentage_sanity_check(percentage, count_columns)

    result = pd.concat([dataframe[info_columns], percentage], axis=1)

    return result


def compute_mean_percentage(dataframe, count_columns, group_columns):
    """
    Compute mean percentage

    Arguments:
    dataframe (pd.DataFrame): dataframe containing row percentages
    count_columns (list): list of columns on which to compute the means
    group_columns (list): columns to group the rows by

    Returns:
    dataframe with mean percentage for each group
    """
    mean_percentage = dataframe.groupby(group_columns)[count_columns].mean()
    percentage_sanity_check(mean_percentage, count_columns)

    return mean_percentage


def compute_percentage(dataframe, count_columns, total_column, info_columns):
    percentage_per_replicate = compute_percentage_per_row(dataframe,
                                                          count_columns,
                                                          total_column,
                                                          info_columns)
    grouped_percentage = compute_mean_percentage(percentage_per_replicate,
                                                 count_columns,
                                                 info_columns)
    return grouped_percentage


def plot_larval_behavior(dataframe, cohort_id, save_dir):
    """
    Plot the proportion of each observed behavior and output it in a .png file.

    Arguments:
    dataframe (pd.DataFrame): dataframe containing the percentages
    cohort_id (str): cohort identification
    save_dir (str): directory to save the output plot.

    Returns:
    None
    """
    cohort_data = dataframe.loc[cohort_id]
    treatments = cohort_data.index.unique(level="TREATMENT")

    fig, axes = plt.subplots(1, len(treatments),
                             figsize=(4 * len(treatments), 4),
                             sharey=False, squeeze=False)
    fig.suptitle(f"[{cohort_id}] - Larval Behavior")

    for ax, treatment in zip(axes[0], treatments):
        treatment_data = cohort_data.loc[treatment]
        treatment_data.plot(kind="bar", stacked=True, ax=ax)
        ax.set(title=treatment,
               xlabel="Larval age",
               ylabel="Percentage", ylim=(0, 100))

    save_path = Path(save_dir)
    save_path.mkdir(exist_ok=True)

    fig.savefig(save_path / f"{cohort_id}_Larval_behavior.png",
                dpi=150,
                bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":

    file_path = config.FILE_PATH
    print(f"Loading coral data from: {file_path}")
    coral_data = load_coral_data(file_path)
    print_info_loaded_data(coral_data)

    info_columns = config.INFO_COLUMNS
    behavior_columns = config.BEHAVIOR_COLUMNS
    total_larvae_per_replicate = config.TOTAL_LARVAE_REPLICATE

    coral_data = data_preparation(coral_data, behavior_columns)

    behavior_columns = behavior_columns + ["NB_DEAD"]

    grouped_percentage = compute_percentage(coral_data,
                                            behavior_columns,
                                            total_larvae_per_replicate,
                                            info_columns)
    print(grouped_percentage)

    plot_larval_behavior(grouped_percentage, "20260307_GFASC_FEF", "./output")