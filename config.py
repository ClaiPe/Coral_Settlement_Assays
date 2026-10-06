# Parameter used to plot the coral settlement data.

FILE_PATH = "data/202603_GFASC_FEF_Settlement_Assays.csv"
# FILE_PATH = "data/test_comma.csv"
# FILE_PATH = "data/empty_file.csv"
# FILE_PATH = "data/exact_columns.csv"

TOTAL_LARVAE_REPLICATE = "TOTAL_LARVAE_SET"

INFO_COLUMNS = ["COHORT_ID", "TREATMENT", "AGE_LARVAE"]

BEHAVIOR_COLUMNS = ["NB_CCA_SETTLERS_TOP",
                    "NB_CCA_SETTLERS_BOTTOM",
                    "NB_PETRIDISH_SETTLERS",
                    "NB_HANGERS",
                    "NB_SWIMMING",
                    "NB_NOT_SWIMMING",
                    "NB_CAULIFLOWERS"]

MANDATORY_COLUMNS = [TOTAL_LARVAE_REPLICATE] + INFO_COLUMNS + BEHAVIOR_COLUMNS + ["NB_REPLICATES"]

OUTPUT_PATH = "./output"
OUTPUT_FORMAT = "png"
OUTPUT_RES = 150
