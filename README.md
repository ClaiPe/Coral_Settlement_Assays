# 🦐 Coral Settlement Assays

A small Python application that turns the results of coral larval settlement
assays into percent stacked bar charts.

For each cohort, it shows how larvae are distributed between behaviors
(settled on CCA, settled on the Petri dish, hanging, swimming, not swimming,
"cauliflowers", dead) at each larval age, with one chart per treatment.

It can be used in two ways:

- **a web app** (Streamlit): upload a CSV file, generate the charts, download them as a ZIP;
- **a command-line script**: read a CSV file and save the charts as PNG images.

## Using the web app

The app is hosted on Streamlit Community Cloud: `https://coral-settlement.streamlit.app/`

Access is restricted: ask the maintainer to invite your e-mail address, then
sign in with that address (a code is sent by e-mail).

1. Click **Browse files** and choose your CSV file.
2. Read the messages: errors are shown in red, warnings in orange.
3. Click **Generate graphs**: one figure per cohort is displayed.
4. Click **Download graphs** to get all figures in a single ZIP file.

If the app has not been used for a while, a "This app has gone to sleep"
page may appear. Click the button to wake it up and wait a few seconds.

**Your data is not stored.** The uploaded file is processed in memory for your
session only. It is never saved on the server or added to the code repository.

## Input file format

- CSV file, with `,` or `;` as separator (detected automatically).
- Decimal separator: `.` (for example `2.65`, not `2,65`).
- Column order does not matter.
- The following 12 columns are required:

| Column | Content |
|---|---|
| `COHORT_ID` | cohort identifier |
| `TREATMENT` | treatment applied |
| `AGE_LARVAE` | age of the larvae |
| `NB_REPLICATES` | replicate identifier |
| `TOTAL_LARVAE_SET` | number of larvae in the replicate |
| `NB_CCA_SETTLERS_TOP` | larvae settled on top of the CCA |
| `NB_CCA_SETTLERS_BOTTOM` | larvae settled under the CCA |
| `NB_PETRIDISH_SETTLERS` | larvae settled on the Petri dish |
| `NB_HANGERS` | hanging larvae |
| `NB_SWIMMING` | swimming larvae |
| `NB_NOT_SWIMMING` | non-swimming larvae |
| `NB_CAULIFLOWERS` | "cauliflower" larvae |

Other columns (for example `START_DATE`, `MONITORING_DATE`,
`PERCENTAGE_SETTLERS`) are accepted but ignored, with a warning.

## How the charts are computed

1. **Dead larvae**: for each replicate,
   `NB_DEAD = TOTAL_LARVAE_SET - (sum of the 7 behavior columns)`.
2. **Invalid rows**: replicates where `NB_DEAD` is negative (more larvae
   counted than set) are removed, and listed in a warning.
3. **Percentages per replicate**: each behavior (and `NB_DEAD`) is divided by
   `TOTAL_LARVAE_SET` and multiplied by 100.
4. **Mean per group**: percentages are averaged over the replicates of each
   cohort × treatment × larval age combination.
5. **Charts**: one figure per cohort, one chart per treatment side by side,
   larval age on the x axis, stacked percentages (0 to 100) on the y axis,
   one legend per figure.

## Errors and warnings

| Situation | Behavior |
|---|---|
| File not found, empty or unreadable | error, processing stops |
| Required column missing | error listing the missing columns |
| Extra columns | warning, columns ignored |
| Negative number of dead larvae | warning listing the rows, rows removed |

## Running locally (for development)

Requirements: Python 3.12.

```bash
# create and activate an environment (conda example)
conda create -n coral-settlement python=3.12
conda activate coral-settlement

# install the dependencies (pinned versions)
pip install -r requirements.txt
```

**Web app:**

```bash
streamlit run app.py
```

**Command line:** set `FILE_PATH` in `config.py`, then run:

```bash
python coral_data_plot.py
```

The PNG images and a ZIP of all images are saved in the `output/` folder.

**Tests:**

```bash
python -m pytest
```

## Project structure

```
app.py                  Streamlit interface (upload, messages, charts, download)
coral_data_plot.py      loading, checks, calculations and plotting
config.py               column names, input file, output folder, format and resolution
tests/                  pytest tests
requirements.txt        Python dependencies with pinned versions
data/                   local input files (ignored by Git)
output/                 images created by the command-line script (ignored by Git)
```

## Configuration

All settings are in `config.py`:

- `FILE_PATH`: input file used by the command-line script;
- `INFO_COLUMNS`, `BEHAVIOR_COLUMNS`, `TOTAL_LARVAE_REPLICATE`, `MANDATORY_COLUMNS`: expected column names;
- `OUTPUT_PATH`, `OUTPUT_FORMAT`, `OUTPUT_RES`: where and how images are saved.

## Known limitations

These points are planned but not handled yet:

- Leading or trailing spaces in values are not cleaned: `"NSW "` and `"NSW"`
  would be treated as two different treatments.
- A typo in a numeric column (for example `3. 1`) is not detected and can
  silently distort the calculations.
- Rows with missing values (NA) are not removed automatically.

Please check your file carefully until these points are addressed.

## License

MIT, see [LICENSE](LICENSE).
