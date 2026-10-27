"""Read NOAA Atlantic HURDAT2 observations without estimating losses."""
from pathlib import Path
from datetime import datetime, timezone
import re

import pandas as pd

SOURCE_URL = "https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2025-092326.txt"
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "raw" / SOURCE_URL.rsplit("/", 1)[1]


def coordinate(value: str, latitude: bool) -> float:
    """Convert a hemisphere coordinate such as 94.8W to signed degrees."""
    hemispheres = "NS" if latitude else "EW"
    if not value or value[-1] not in hemispheres:
        raise ValueError(f"Invalid coordinate: {value}")
    magnitude = float(value[:-1])
    if not 0 <= magnitude <= (90 if latitude else 180):
        raise ValueError(f"Coordinate out of range: {value}")
    return -magnitude if value[-1] in "SW" else magnitude


def parse_hurdat(text: str) -> pd.DataFrame:
    """Check storm record counts and preserve every observation, including landfalls."""
    records = []
    remaining = 0
    storm_id = name = ""
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        fields = [field.strip() for field in line.split(",")]
        try:
            if re.fullmatch(r"AL\d{6}", fields[0]):
                if remaining:
                    raise ValueError("Previous storm has fewer observations than declared")
                storm_id, name = fields[:2]
                remaining = int(fields[2])
                if remaining <= 0:
                    raise ValueError("Storm record count must be positive")
                continue
            if not storm_id or remaining <= 0 or len(fields) < 8:
                raise ValueError("Unexpected observation or incomplete row")
            wind, pressure = int(fields[6]), int(fields[7])
            records.append({
                "storm_id": storm_id, "name": name, "year": int(storm_id[-4:]),
                "time_utc": datetime.strptime(fields[0] + fields[1], "%Y%m%d%H%M").replace(tzinfo=timezone.utc),
                "record_identifier": fields[2], "status": fields[3],
                "latitude": coordinate(fields[4], True),
                "longitude": coordinate(fields[5], False),
                "wind_knots": None if wind < 0 else wind,
                "pressure_mb": None if pressure < 0 else pressure,
            })
            remaining -= 1
        except (ValueError, IndexError) as error:
            raise ValueError(f"HURDAT2 line {line_number}: {error}") from error
    if remaining or not records:
        raise ValueError("Empty or truncated HURDAT2 file")
    frame = pd.DataFrame(records)
    if frame.duplicated(["storm_id", "time_utc"]).any():
        raise ValueError("Duplicate storm timestamps")
    return frame.sort_values(["storm_id", "time_utc"]).reset_index(drop=True)


def load_tracks(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load the downloaded source file from disk."""
    return parse_hurdat(path.read_text(encoding="utf-8"))


def summarize_claims(matched: pd.DataFrame) -> pd.DataFrame:
    """Sum only available reported payment components and expose missingness."""
    fields = ['amountPaidOnBuildingClaim','amountPaidOnContentsClaim','amountPaidOnIncreasedCostOfComplianceClaim']
    frame = matched.copy()
    frame[fields] = frame[fields].apply(pd.to_numeric, errors='coerce')
    frame['missing_payment'] = frame[fields].isna().any(axis=1)
    frame['invalid_payment'] = frame.missing_payment | (frame[fields] < 0).any(axis=1)
    frame['available_components'] = frame[fields].notna().sum(axis=1)
    frame['paid_loss'] = frame[fields].sum(axis=1, min_count=1)
    return frame.groupby(['storm_id','county_fips']).agg(
        claim_count=('id','size'), paid_loss=('paid_loss',lambda x: x.sum(min_count=1)),
        invalid_payment_count=('invalid_payment','sum'),missing_payment_count=('missing_payment','sum'),
        available_components=('available_components','sum')).reset_index()
