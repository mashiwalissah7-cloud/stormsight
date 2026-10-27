# StormSight

A research and education tool for exploring hurricane flood insurance losses. It is not a commercial catastrophe model.

## Current status

The app displays historical NOAA storm observations on a map. Users can choose a season and storm, inspect measurements, and download the selected observations. Loss predictions, portfolio calculations, and AI briefings are not implemented yet.

## Run locally

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

## Verified data source

Provider: NOAA National Hurricane Center.

Dataset: Atlantic HURDAT2, covering 1851 through 2025. The archive describes this release as updated on September 23, 2026.

[Source file](https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2025-092326.txt)

[Format documentation](https://www.nhc.noaa.gov/data/hurdat/hurdat2-format-atl-1851-2021.pdf)

Retrieved on October 27, 2026. The original file is stored in `data/raw` unchanged.

SHA256: `75202780ce56c8458f16fbef5fb8a026b99b00878dbb95c458211b3e6ef125b4`

The reader loaded 55,524 observations across 1,988 storms and checked the declared observation counts. Times are UTC. Wind is measured in knots and pressure in millibars. Negative measurement sentinels become missing values. Special observations, including landfall records between regular observation times, are retained.

## Checks

```sh
.venv/bin/python -m unittest discover -s tests -v
```

The reader checks coordinates, missing pressure, record counts, duplicate timestamps, and empty input. These checks test data handling only. They do not establish prediction accuracy.

## Limitations

This is historical replay, not a live forecast. Connecting recorded positions does not show a damage footprint. Storm tracks alone cannot establish flood damage or insured losses. Some older measurements are missing. Map tiles require an internet connection and are provided by CARTO and OpenStreetMap.

## Next steps

Verify FEMA claims and county data, define and test storm matching, evaluate a loss model on unseen storms, and then connect an NVIDIA model through Nebius Token Factory.
