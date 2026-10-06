import pandas as pd
import pytest

from coral_data_plot import (InvalidDataError, 
                             check_column_content, compute_percentage_per_row)

def test_all_mandatory_columns_available():
    mandatory_columns = ["TOTAL_LARVAE_SET", "COHORT_ID", "TREATMENT",
                         "NB_REPLICATES", "AGE_LARVAE", "NB_CCA_SETTLERS_TOP",
                         "NB_CCA_SETTLERS_BOTTOM", "NB_PETRIDISH_SETTLERS", "NB_HANGERS",
                         "NB_SWIMMING", "NB_NOT_SWIMMING", "NB_CAULIFLOWERS"]
    good_data = pd.DataFrame({"TOTAL_LARVAE_SET": [10], 
                              "COHORT_ID": ["1_FEF"],
                              "TREATMENT": ["NSW"],
                              "NB_REPLICATES": [3],
                              "AGE_LARVAE": [2.1], 
                              "NB_CCA_SETTLERS_TOP": [3],
                              "NB_CCA_SETTLERS_BOTTOM": [0],
                              "NB_PETRIDISH_SETTLERS": [1],
                              "NB_HANGERS": [0],
                              "NB_SWIMMING": [3],
                              "NB_NOT_SWIMMING": [1],
                              "NB_CAULIFLOWERS": [2] })
    result = check_column_content(good_data, mandatory_columns)
    assert result == []


def test_not_all_mandatory_columns_available_raises_error():
    mandatory_columns = ["TOTAL_LARVAE_SET", "COHORT_ID", "TREATMENT",
                         "NB_REPLICATES", "AGE_LARVAE", "NB_CCA_SETTLERS_TOP",
                         "NB_CCA_SETTLERS_BOTTOM", "NB_PETRIDISH_SETTLERS", "NB_HANGERS",
                         "NB_SWIMMING", "NB_NOT_SWIMMING", "NB_CAULIFLOWERS"]
    bad_data = pd.DataFrame({"COHORT_ID": ["1_FEF"],
                              "TREATMENT": ["NSW"],
                              "AGE_LARVAE": [2.1], 
                              "NB_CCA_SETTLERS_TOP": [3],
                              "NB_PETRIDISH_SETTLERS": [1],
                              "NB_HANGERS": [0],
                              "NB_SWIMMING": [3],
                              "NB_NOT_SWIMMING": [1],
                              "NB_CAULIFLOWERS": [2] })
    with pytest.raises(InvalidDataError):
        check_column_content(bad_data, mandatory_columns)


def test_percentage_computation_correct():
    good_data = pd.DataFrame({"TOTAL_LARVAE_SET": [10], 
                            "COHORT_ID": ["1_FEF"],
                            "TREATMENT": ["NSW"],
                            "NB_REPLICATES": [3],
                            "AGE_LARVAE": [2.1], 
                            "NB_CCA_SETTLERS_TOP": [7],
                            "NB_HANGERS": [0],
                            "NB_SWIMMING": [3]})
    result = compute_percentage_per_row(good_data, 
                                count_columns=["NB_CCA_SETTLERS_TOP", "NB_HANGERS", "NB_SWIMMING"],
                                total="TOTAL_LARVAE_SET",
                                info_columns=["COHORT_ID", "TREATMENT", "AGE_LARVAE"])
    assert result.loc[0, ["NB_CCA_SETTLERS_TOP", 
                      "NB_HANGERS",
                      "NB_SWIMMING"]].tolist() == pytest.approx([70, 0, 30])
