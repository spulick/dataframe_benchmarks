import pandas as pd
import requests
import os
import zipfile

import time

from sklearn.metrics import mean_squared_error

import matplotlib.pyplot as plt
import seaborn as sns

web_addr = "https://microdata.worldbank.org/index.php/catalog/5908/download/62511"

# Download the data

if not os.path.exists("./Data/WLD_2023_SYNTH-CEN-HLD-EN_v01_M.dta"):
    os.makedirs("./Data", exist_ok=True)
    
    with open("./dta.zip", "wb") as f:
        f.write(requests.get(web_addr).content)

    with zipfile.ZipFile("./dta.zip", 'r') as zip_ref:
        zip_ref.extractall("./Data")

    # delete the zip file

    os.remove("./dta.zip")

# Benchmark from here

# Load the data

t = time.process_time()

hld = pd.read_stata("./Data/WLD_2023_SYNTH-CEN-HLD-EN_v01_M.dta")
ind = pd.read_stata("./Data/WLD_2023_SYNTH-CEN-IND-EN_v01_M.dta")
margins = pd.read_csv("./Data/margins.csv")

read1_time = time.process_time() - t

# Merge the data

t = time.process_time()

ind = ind.merge(hld, on="hid", how="left")

merge_time = time.process_time() - t

# run sampling

population = pd.DataFrame(columns=ind.columns)
dummy_margins = margins.copy()
dummy_margins["count"] = 0

def margins_compute(population):

    pop_margins = population.groupby(["sex", "age", "marstat", "occupation", "hhsize", "electricity", "bank"]).size().reset_index(name="count")
    pop_margins = pop_margins.concat(dummy_margins).reset_index(drop=True)
    
    pop_margins = pop_margins.groupby(["sex", "age", "marstat", "occupation", "hhsize", "electricity", "bank"]).agg({"count": "sum"}).reset_index()

    return pop_margins

t = time.process_time()

while mean_squared_error(margins_compute(population), margins) > 0.001:
    # run sampling
    
    gap = margins_compute(population)["count"].sum() - margins["count"].sum()

    sample = ind.sample(n=gap, replace=True)

    population = pd.concat([population, sample], ignore_index=True)

    new_margins = margins_compute(population)

    new_margins["count"] = margins["count"] - new_margins["count"] 

    population = population.groupby(["sex", "age", "marstat", "occupation", "hhsize", "electricity", "bank"]).apply(lambda x: x.sample(n=margins.loc[x.name, "count"], replace=False) if new_margins.loc[x.name, "count"] > 0 else x).reset_index(drop=True)

sampling_time = time.process_time() - t

# write the synthetic data

os.makedirs("./Synthetic", exist_ok=True)

t = time.process_time()

population.to_csv("./Synthetic/synthetic_data.csv", index=False)
population.to_stata("./Synthetic/synthetic_data.dta", write_index=False)
population.to_excel("./Synthetic/synthetic_data.xlsx", index=False)
population.to_pickle("./Synthetic/synthetic_data.pkl")
population.to_parquet("./Synthetic/synthetic_data.parquet", index=False)

write_time = time.process_time() - t

# load the synthetic data

synthetic = pd.read_csv("./Synthetic/synthetic_data.csv")

# generate analyses and graphs

t = time.process_time()

# Descriptive Statistics
print("Descriptive Statistics:")
print(synthetic.describe())

# Distribution Plots
def plot_distribution(data, column, title):
    plt.figure(figsize=(10, 6))
    sns.histplot(data[column], kde=True)
    plt.title(title)
    plt.xlabel(column)
    plt.ylabel('Frequency')
    plt.show()

plot_distribution(synthetic, 'age', 'Age Distribution')
plot_distribution(synthetic, 'hhsize', 'Household Size Distribution')

# Correlation Matrix
plt.figure(figsize=(12, 8))
correlation_matrix = synthetic.corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Correlation Matrix')
plt.show()

analysis_time = time.process_time() - t

# write report

report = {

    device = os.uname(),

    "read1_time": read1_time,
    "merge_time": merge_time,
    "sampling_time": sampling_time,
    "write_time": write_time,
    "analysis_time": analysis_time
}


os.makedirs("./Reports", exist_ok=True)



