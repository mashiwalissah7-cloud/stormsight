"""Rebuild the retrospective benchmark from the prepared study table."""
import json
import pandas as pd
from src.stormsight.model import fit_benchmark
if __name__=='__main__':
    table=pd.read_csv('data/processed/study_counties.csv',dtype={'county_fips':str})
    print(json.dumps(fit_benchmark(table),indent=2))
