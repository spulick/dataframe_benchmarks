import pandas as pd
import requests
import os
import zipfile

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

hld = pd.read_stata("./Data/WLD_2023_SYNTH-CEN-HLD-EN_v01_M.dta")
ind = pd.read_stata("./Data/WLD_2023_SYNTH-CEN-IND-EN_v01_M.dta")
margins = pd.read_csv("margins.csv")

# Merge the data

ind = ind.merge(hld, on="hid", how="left")

# run sampling

# write the synthetic data

# load the synthetic data

# generate analyses and graphs



