import streamlit as st

import config
from coral_data_plot import InvalidDataError, prepare_data_for_plotting

st.title("Coral Settlement Assays Experiment Visualization")
st.write("Upload your coral settlement assays data to plot larval behavior proportions.")
st.markdown(f"""
**Expected file format:**
- CSV file, separated by ',' or ';'
- Decimal separator must be '.'
- The file must at least contain the following data (12 columns):
    - the cohort id in a column "COHORT_ID"
    - the treatment applied in a column "TREATMENT"
    - the age of larvae in a column "AGE_LARVAE"
    - the replicate ID in a column "NB_REPLICATES"
    - the number of larvae in each replicate in a column "TOTAL_LARVAE_SET"
    - the number of larvae observed in each developement stage including: {config.BEHAVIOR_COLUMNS}
""")

uploaded_file = st.file_uploader("Choose a coral settlement assays file", type="csv")

if uploaded_file is not None:
    st.success(f"File received: {uploaded_file.name}")
    try:
        grouped_percentage, warnings_list = prepare_data_for_plotting(uploaded_file)
    except InvalidDataError as error:
        st.error(str(error))
        st.stop()
    for warning in warnings_list:
        st.warning(warning)

    st.dataframe(grouped_percentage.round(0))