"""Portfolio values within the study corridor, without invented loss rates."""
from io import StringIO
import numpy as np
import pandas as pd


def read_portfolio(text, known_fips):
    if len(text.encode('utf-8')) > 2_000_000:
        raise ValueError('Upload must be smaller than 2 MB.')
    try:
        frame = pd.read_csv(StringIO(text), dtype={'county_fips':str})
    except Exception as error:
        raise ValueError('The upload must be a readable CSV file.') from error
    if set(frame.columns) != {'county_fips','insured_value'} or frame.empty or len(frame)>10000:
        raise ValueError('Use exactly county_fips and insured_value columns, with 1 to 10,000 rows.')
    frame.county_fips = frame.county_fips.str.strip()
    if not frame.county_fips.str.fullmatch(r'\d{5}').all():
        raise ValueError('County FIPS codes must have five digits, including leading zeros.')
    if not frame.county_fips.isin(known_fips).all():
        raise ValueError('One or more county codes are not in the Census county file.')
    frame.insured_value = pd.to_numeric(frame.insured_value, errors='coerce')
    if not np.isfinite(frame.insured_value).all() or (frame.insured_value<0).any():
        raise ValueError('Insured values must be finite, nonnegative numbers.')
    if frame.insured_value.sum()>1e15:
        raise ValueError('Portfolio total is too large for this research demo.')
    return frame.groupby('county_fips',as_index=False).insured_value.sum()


def portfolio_exposure(portfolio, county_results):
    merged = portfolio.merge(county_results, on='county_fips', how='left', validate='one_to_one')
    merged['in_corridor'] = merged.min_distance_km.notna()
    return merged, float(merged.loc[merged.in_corridor,'insured_value'].sum())
