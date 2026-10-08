from pathlib import Path

import streamlit as st
import matplotlib.pyplot as plt

import config
from coral_data_plot import (InvalidDataError,
                             prepare_data_for_plotting, plot_larval_behavior,
                             zippack_figures)

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
    - the number of larvae observed in each development stage including: {", ".join(config.BEHAVIOR_COLUMNS)}
""")

uploaded_file = st.file_uploader("Choose a coral settlement assays file", type="csv")

if uploaded_file is not None:
    st.success(f"File received: {uploaded_file.name}")

    mandatory_columns = config.MANDATORY_COLUMNS
    info_columns = config.INFO_COLUMNS
    behavior_columns = config.BEHAVIOR_COLUMNS
    total_larvae_per_replicate = config.TOTAL_LARVAE_REPLICATE
    output_format = config.OUTPUT_FORMAT
    output_res = config.OUTPUT_RES

    try:
        grouped_percentage, warnings_list = prepare_data_for_plotting(uploaded_file,
                                                                      mandatory_columns,
                                                                      info_columns,
                                                                      behavior_columns,
                                                                      total_larvae_per_replicate)
    except InvalidDataError as error:
        st.error(str(error))
        st.stop()
    for warning in warnings_list:
        st.warning(warning)

    st.dataframe(grouped_percentage.round(0))

    if st.button("Generate graphs"):
        st.session_state["graphs_requested"] = True

    if st.session_state.get("graphs_requested", False):
        cohorts = grouped_percentage.index.unique(level="COHORT_ID")

        with st.spinner("Plotting larval behavior for each cohort..."):
            zip_bytes = zippack_figures(grouped_percentage,
                                        output_format, output_res)
            output_file_name = f"{Path(uploaded_file.name).stem}_plot.zip"

            st.download_button(
                label="Download graphs",
                data=zip_bytes,
                file_name=output_file_name,
                mime="application/zip")

            for cohort in cohorts:
                figure, _ = plot_larval_behavior(grouped_percentage, cohort)
                st.pyplot(figure)
                plt.close(figure)
