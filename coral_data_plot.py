from pathlib import Path
import csv

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

import config


class InvalidDataError(Exception):
    """Error caused by an invalid data file"""


def load_coral_data(file_path):
    """
    Load coral data from a CSV file.

    Parameters:
    file_path (str): The path to the CSV file containing coral data.
    Both comma and semicolon separators are allowed.

    Returns:
    pd.DataFrame: A DataFrame containing the loaded coral data.
    """
    try:
        coral_data = pd.read_csv(file_path, sep=None, engine="python")
        return coral_data

    except FileNotFoundError:
        raise InvalidDataError(f"The file at {file_path} was not found.")

    except pd.errors.EmptyDataError:
        raise InvalidDataError(f"The file at {file_path} is empty.")

    except pd.errors.ParserError:
        raise InvalidDataError("There was a parsing error while reading the file.")

    except csv.Error:
        raise InvalidDataError("Separator not detected or empty file")


def check_column_content(dataframe, mandatory_columns):
    """
    Check if the mandatory columns are present in the dataframe 
    and if there are additional columns

    Arguments:
    dataframe (pd.DataFrame): the dataframe containing the data
    mandatory_columns (list): list of mandatory columns

    Returns:
    Warning message to inform the user on column content.

    Raises:
    InvalidDataError if mandatory column missing.
    """
    warnings = []
    missing_columns = [column for column in mandatory_columns
                       if column not in dataframe.columns]
    if missing_columns:
        raise InvalidDataError(f"Missing mandatory columns:"
                               f"{", ".join(missing_columns)}")

    additional_columns = [column for column in dataframe.columns
                          if column not in mandatory_columns]
    if additional_columns:
        warnings.append(f"Additional columns detected: "
                        f"{", ".join(additional_columns)}.\n"
                        "These columns will be ignored.")
    return warnings


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


def data_preparation(dataframe, behavior_columns, id_columns, total_larvae_column="TOTAL_LARVAE_SET"):
    """
    Prepare the coral data for analysis.

    Parameters:
    dataframe (pd.DataFrame): The DataFrame containing the loaded data
    behavior_columns (list): Names of column for behavior data
    id_columns (list): Columns necessary to identify a row
    total_larvae_column (str): Name of the column with total number of larvae in the replicate

    What it does:
    Add a NB_DEAD column containing the number of dead larvae in the batch.
    Remove the rows where NB_DEAD < 0

    Returns:
    The updated dataframe and associated warnings when necessary.
    """
    warnings = []

    settled_larvae = dataframe[behavior_columns].sum(axis=1)
    dataframe["NB_DEAD"] = dataframe[total_larvae_column] - settled_larvae

    # Data check
    negative_dead_mask = dataframe["NB_DEAD"] < 0
    if negative_dead_mask.any():
        negative_dead_rows = dataframe.loc[negative_dead_mask, id_columns]
        negative_dead_rows_text = negative_dead_rows.to_string(index=False)
        warnings.append(
            f"{negative_dead_mask.sum()} rows were removed "
            f"because the number of dead larvae was negative:\n{negative_dead_rows_text}")

        # remove the problematic rows:
        dataframe = dataframe.drop(dataframe[negative_dead_mask].index)

    return dataframe, warnings


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


def plot_larval_behavior(dataframe, cohort_id):
    """
    Plot the proportion of each observed behavior.

    Arguments:
    dataframe (pd.DataFrame): dataframe containing the percentages
    cohort_id (str): cohort identification

    Returns:
    fig (matplotlib.figure.Figure) containing the plots
    fig name (str).
    """
    cohort_data = dataframe.loc[cohort_id]
    treatments = cohort_data.index.unique(level="TREATMENT")

    fig, axes = plt.subplots(1, len(treatments),
                             figsize=(4 * len(treatments), 4),
                             sharey=False, squeeze=False)
    fig.suptitle(f"[{cohort_id}] - Larval Behavior")

    for ax, treatment in zip(axes[0], treatments):
        treatment_data = cohort_data.loc[treatment]
        treatment_data.plot(kind="bar", stacked=True, ax=ax,
                            legend=False)
        ax.set(title=treatment,
               xlabel="Larval age",
               ylabel="Percentage", ylim=(0, 100))

    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles,
               labels,
               loc="center left",
               bbox_to_anchor=(1, 0.5))

    fig_name = f"{cohort_id}_Larval_behavior"

    return fig, fig_name


def save_figure(fig, fig_name, save_dir, format="png"):
    """
    Save a figure in the output directory

    Arguments:
    fig (matplotlib.figure.Figure): figure to save
    fig_name (str): name of output file
    save_dir (str): directory to save the output fig.

    Returns:
    None
    """
    save_path = Path(save_dir)
    save_path.mkdir(exist_ok=True)

    fig.savefig(save_path / f"{fig_name}.{format}",
                dpi=150,
                bbox_inches="tight")
    plt.close(fig)


def main():
    """
    Plot larval behavior for each cohort and each treatment.
    The function reads the data specified in the config 
    and saves a plot per cohort in the output folder.
    """
    file_path = config.FILE_PATH
    mandatory_columns = config.MANDATORY_COLUMNS
    info_columns = config.INFO_COLUMNS
    behavior_columns = config.BEHAVIOR_COLUMNS
    total_larvae_per_replicate = config.TOTAL_LARVAE_REPLICATE

    # Loading data
    try:
        print(f"Loading coral data from: {file_path}")
        coral_data = load_coral_data(file_path)
    except InvalidDataError as error:
        print(f"ERROR: {error}")
        return
    # print_info_loaded_data(coral_data)

    try:
        columns_check = check_column_content(coral_data, mandatory_columns)
    except InvalidDataError as error:
        print(f"ERROR: {error}")
        return
    for warning in columns_check:
        print(f"WARNING: {warning}")

    # Data preprocessing
    coral_data, warnings = data_preparation(coral_data, 
                                            behavior_columns,
                                            info_columns + ["NB_REPLICATES"])
    # print warnings
    for warning in warnings:
        print(f"WARNING: {warning}")

    behavior_columns = behavior_columns + ["NB_DEAD"]

    grouped_percentage = compute_percentage(coral_data,
                                            behavior_columns,
                                            total_larvae_per_replicate,
                                            info_columns)
    print(grouped_percentage)

    cohorts = grouped_percentage.index.unique(level="COHORT_ID")

    for cohort in tqdm(cohorts,
                       desc="Plotting larval behavior for each cohort"):
        figure, fig_name = plot_larval_behavior(grouped_percentage, cohort)
        save_figure(figure, fig_name, config.OUTPUT_PATH)


if __name__ == "__main__":
    main()
