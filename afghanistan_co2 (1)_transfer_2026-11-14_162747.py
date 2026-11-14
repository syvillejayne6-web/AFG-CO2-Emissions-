# Country-Level CO2 Emissions Analysis: Afghanistan (AFG)
# Python conversion of the supplied analyze_co2.R script.
# Run in Pydroid 3. Uses the Our World in Data CO2 dataset.

import os
import urllib.request
import pandas as pd
import matplotlib.pyplot as plt

country_code = "AFG"
country_name = "Afghanistan"
start_year = 1990
end_year = 2024

data_url = "https://catalog.ourworldindata.org/garden/emissions/2026-11-10/owid_co2/owid_co2.csv"
raw_file = "data/owid-co2-data.csv"
country_file = "data/AFG_co2.csv"

# Create the output folders.
for folder in ("data", "figures", "results"):
    os.makedirs(folder, exist_ok=True)

# Download the source dataset only if it is not already saved.
if not os.path.exists(raw_file):
    print("Downloading the Our World in Data CO2 dataset. Please wait...")
    urllib.request.urlretrieve(data_url, raw_file)

print("Reading the dataset...")
all_data = pd.read_csv(raw_file)
required_columns = ["iso_code", "country", "year", "co2", "co2_per_capita"]
missing_columns = [column for column in required_columns if column not in all_data.columns]
if missing_columns:
    raise ValueError(
        "The downloaded dataset is missing required columns: "
        + ", ".join(missing_columns)
        + ". Check the OWID codebook and update the script if column names changed."
    )

# Filter Afghanistan and the requested years. Missing values remain missing (NaN), not zero.
country_data = all_data.loc[
    (all_data["iso_code"] == country_code)
    & (all_data["year"] >= start_year)
    & (all_data["year"] <= end_year),
    required_columns,
].copy()
country_data = country_data.sort_values("year").reset_index(drop=True)
if country_data.empty:
    raise ValueError("No rows found for AFG in the selected year range.")

country_data.to_csv(country_file, index=False, na_rep="")

# Calculate annual percentage change only for consecutive years with valid, non-zero values.
country_data["annual_change_percent"] = float("nan")
for i in range(1, len(country_data)):
    current_year = country_data.loc[i, "year"]
    previous_year = country_data.loc[i - 1, "year"]
    current_co2 = country_data.loc[i, "co2"]
    previous_co2 = country_data.loc[i - 1, "co2"]
    if (
        current_year == previous_year + 1
        and pd.notna(current_co2)
        and pd.notna(previous_co2)
        and previous_co2 != 0
    ):
        country_data.loc[i, "annual_change_percent"] = (
            (current_co2 - previous_co2) / previous_co2
        ) * 100

valid_co2 = country_data.loc[country_data["co2"].notna()].copy()
valid_pc = country_data.loc[country_data["co2_per_capita"].notna()].copy()
if valid_co2.empty:
    raise ValueError("No valid annual CO2 observations were found for Afghanistan.")

first_row = valid_co2.iloc[0]
latest_row = valid_co2.iloc[-1]
peak_row = valid_co2.loc[valid_co2["co2"].idxmax()]
endpoint_change = (
    ((latest_row["co2"] - first_row["co2"]) / first_row["co2"]) * 100
    if first_row["co2"] != 0
    else float("nan")
)
latest_pc = valid_pc.iloc[-1]["co2_per_capita"] if not valid_pc.empty else float("nan")
latest_pc_year = int(valid_pc.iloc[-1]["year"]) if not valid_pc.empty else None

summary_table = pd.DataFrame([{
    "country": country_name,
    "iso_code": country_code,
    "first_valid_year": int(first_row["year"]),
    "first_valid_co2_million_tonnes": first_row["co2"],
    "latest_valid_year": int(latest_row["year"]),
    "latest_valid_co2_million_tonnes": latest_row["co2"],
    "endpoint_percent_change": endpoint_change,
    "peak_year": int(peak_row["year"]),
    "peak_co2_million_tonnes": peak_row["co2"],
    "latest_per_capita_year": latest_pc_year,
    "latest_co2_per_capita_tonnes": latest_pc,
}])
summary_table.to_csv("results/AFG_summary.csv", index=False, na_rep="")
country_data[["year", "co2", "co2_per_capita", "annual_change_percent"]].to_csv(
    "results/AFG_yearly_changes.csv", index=False, na_rep=""
)

# Plot 1: annual total CO2 emissions (million tonnes).
plt.figure(figsize=(10, 6))
plt.plot(valid_co2["year"], valid_co2["co2"], marker="o")
plt.title("Annual CO2 Emissions - Afghanistan (AFG)")
plt.xlabel("Year")
plt.ylabel("CO2 emissions (million tonnes)")
plt.grid(True)
plt.tight_layout()
plt.savefig("figures/AFG_annual_co2.png", dpi=130)
plt.close()

# Plot 2: annual CO2 emissions per capita (tonnes per person).
if not valid_pc.empty:
    plt.figure(figsize=(10, 6))
    plt.plot(valid_pc["year"], valid_pc["co2_per_capita"], marker="o")
    plt.title("CO2 Emissions per Capita - Afghanistan (AFG)")
    plt.xlabel("Year")
    plt.ylabel("CO2 emissions per capita (tonnes per person)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("figures/AFG_per_capita.png", dpi=130)
    plt.close()

# Plot 3: year-over-year percentage change for adjacent years with valid observations.
valid_change = country_data.loc[country_data["annual_change_percent"].notna()].copy()
if not valid_change.empty:
    plt.figure(figsize=(10, 6))
    plt.bar(valid_change["year"], valid_change["annual_change_percent"])
    plt.axhline(y=0, linestyle="--")
    plt.title("Year-over-Year Change in CO2 Emissions - Afghanistan (AFG)")
    plt.xlabel("Year")
    plt.ylabel("Change from previous year (%)")
    plt.grid(True, axis="y")
    plt.tight_layout()
    plt.savefig("figures/AFG_annual_change.png", dpi=130)
    plt.close()

# Save basic Python environment information in place of R's sessionInfo().
with open("results/session_info.txt", "w", encoding="utf-8") as output:
    output.write(f"Python version: {os.sys.version}\n")
    output.write(f"Pandas version: {pd.__version__}\n")
    output.write(f"Matplotlib version: {plt.matplotlib.__version__}\n")

print("\nAFGHANISTAN CO2 EMISSIONS ANALYSIS COMPLETE")
print(summary_table.to_string(index=False))
print("\nFiles saved in the data/, figures/, and results/ folders.")
print(f"First valid year: {int(first_row['year'])}; latest valid year: {int(latest_row['year'])}")
print(f"Endpoint change (%): {endpoint_change:.2f}")
print(f"Peak year: {int(peak_row['year'])}")
