# StormSight

**[Live app](https://stormsight-hurricane.streamlit.app/)** · [MIT license](LICENSE) · [Setup guide](docs/SETUP.md) · [Project handoff](PROJECT_HANDOFF.md)

StormSight helps students and researchers connect an observed hurricane track with county flood insurance claims, inspect a small predictive model, and see its largest mistakes.

**Working locally:** historical maps, county estimates, portfolio corridor screening, data provenance, and a benchmark on five unseen storms. **Verified live on October 27, 2026:** an NVIDIA Nemotron 3 Super briefing (`nvidia/nemotron-3-super-120b-a12b`) through Nebius Token Factory, with every prose check passing. The public app at https://stormsight-hurricane.streamlit.app/ ran the same live briefing successfully. **Demo video:** https://youtu.be/GSQdjodEvrk. The optional Tavily lookup is implemented but has not been tested with a live key.

This is a research prototype. It is not a live forecast, commercial catastrophe model, insurance quote, or emergency guidance.

## How StormSight uses NVIDIA Nemotron and Nebius Token Factory

**Model:** NVIDIA Nemotron 3 Super, `nvidia/nemotron-3-super-120b-a12b`, served by Nebius Token Factory through its OpenAI compatible endpoint `https://api.tokenfactory.nebius.com/v1/`.

**What Nemotron does in the app**

1. **Plans.** When a user clicks Generate Nemotron briefing, Nemotron returns a JSON plan choosing which evidence tools to call from a fixed allowlist (`get_storm_track`, `predict_county_losses`, `list_storms`, and optional portfolio and source tools). Tools are bound to the selected storm, so the model cannot choose files, URLs, or code.
2. **Explains.** Python runs the chosen tools and renders every number and table. Nemotron then writes three qualitative fields: a summary, the key uncertainties, and what to watch.
3. **Is checked.** Any digit, number word, or link in the prose is rejected and sent back with the exact reason, for up to three attempts. Replies that wrap JSON in reasoning tags or code fences are unwrapped first. The full tool trace, including the model ID, is shown in the app.

Code: `src/stormsight/agent.py` (`generate_briefing`) and the briefing section of `app.py`.

**Where Token Factory helped**

- No GPU or model hosting was needed. The standard `openai` Python client worked by changing only the base URL and model ID, so the agent was running within minutes of creating a key.
- The hosted app calls Token Factory directly from Streamlit Community Cloud, with the key stored in Streamlit Secrets, never in the repository.
- Pay per token billing, funded by Nebius Builder Program credits, made it practical to offer live briefings to judges. The app caps use at three briefings per visit and 100 per day, and reuses a briefing for the same storm.

Live briefings for Helene, Milton, Ian, and Idalia passed every check on October 27, 2026; Helene was run both locally and on the hosted app, the others on the hosted app. No other Nebius services are used. Hosting is Streamlit Community Cloud, and tests run on GitHub Actions.

## Try the app

Tested locally with Python 3.14.6. The source snapshots and trained benchmark are included, so no data download or API key is needed to explore the app.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

Open the localhost address printed by Streamlit. Map tiles require internet access. The calculations use local files.

1. Start with Helene in the 2024 season. Inspect its observed track and nearby county points.
2. Read the county estimates and expand the observed claims comparison. Estimates, observations, and empirical ranges are distinct.
3. Open Portfolio and use the clearly labelled fictional sample. It reports insured value near the track, not portfolio losses.
4. Open Does it work? Compare the baseline, model errors, storm totals, and largest misses.
5. Connect Nebius only through the private configuration described in [SETUP.md](docs/SETUP.md). Never paste secrets into a repository or project description.

## What the model estimates

The targets are matched NFIP claim record counts and sums of available reported building, contents, and increased cost of compliance payments. These are not total hurricane damage, unique properties, ultimate settled losses, or private insurance losses.

A county enters the study when its Census internal point is within 250 km of an hourly interpolated observed storm center. Claims are matched by county and loss date from the first nearby day through three days after the last nearby day. Matching checks all nearby storms during 2011 through 2024, including storms outside the selected cohort. Ambiguous claim matches are excluded, and affected county targets are excluded from evaluation. Proximity and dates do not establish causation.

Available payment components are summed with signed adjustments preserved. Missing fields are counted and remain unestimated. County sums may therefore be incomplete. Negative county sums and targets with claims but no available payment components are excluded. Counties with no matched records have zero matched records and payments under this study definition.

The seven predictors are track distance, nearby maximum wind, nearby duration, log land area, water fraction, latitude, and longitude. The model has no rainfall, surge, coastal classification, or historical NFIP policy exposure denominator. Current NRI scores are context only and never enter the model.

## Actual benchmark results

The cohort has 16 storms and 6,460 county and storm rows, of which 6,299 are eligible. The split was fixed before model fitting:

| Split | Storms | Eligible county rows |
| :--- | :--- | ---: |
| Train | Irene 2011, Isaac and Sandy 2012, Matthew 2016, Harvey and Irma 2017, Florence and Michael 2018 | 3,322 |
| Calibration | Dorian 2019, Laura and Sally 2020 | 1,047 |
| Final test | Ida 2021, Ian 2022, Idalia 2023, Helene and Milton 2024 | 1,930 |

A mean baseline is compared with Poisson histogram gradient boosting. Selection uses calibration mean absolute error, separately for each target. Final test targets do not control fitting, model choice, or interval widths. No tuning was performed on the final test storms.

| Final test measure | Mean baseline | Gradient boosting |
| :--- | ---: | ---: |
| Claim count mean absolute error | 165.12 records | 87.23 records |
| Reported payment mean absolute error | $12,702,102 | $7,521,607 |
| Claim count RMSLE | 4.327 | 1.716 |
| Reported payment RMSLE | 14.267 | 9.468 |

Lower is better. The model improves average error but **severely underestimates several large storm totals**. For example, over eligible county targets, Helene has about $6.24 billion in matched reported payments versus a $200.59 million model total. Ian has about $4.73 billion observed versus $511.70 million estimated. The model is not ready for operational or financial decisions.

Ranges use the 90th percentile absolute calibration residual, symmetrically around each estimate with a lower floor of zero. Measured final test coverage is 87.77% for claim counts and 89.12% for payments. These are empirical results, not guaranteed confidence bounds. County errors are correlated within storms. Full observed tracks make this a retrospective benchmark, not a forecast validation.

Exact metrics, predictions, storm totals, source manifests, and an independent county reconciliation are in `data/processed`. The first complete case target definition was discarded after an audit showed severe exclusion bias. The available component target above is the documented correction; preliminary metrics must not be cited.

## Verified public sources

Snapshot retrieved October 27, 2026. Source URLs, dates, and checksums are saved in the manifests.

| Provider | Source | Use |
| :--- | :--- | :--- |
| NOAA NHC | [Atlantic HURDAT2](https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2025-092326.txt), 1851 through 2025 | 55,524 observations across 1,988 storms |
| U.S. Census Bureau | [2025 county Gazetteer](https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2025_Gazetteer/2025_Gaz_counties_national.zip) | 3,222 county internal points and area measurements |
| FEMA | [NFIP redacted claims v3](https://www.fema.gov/openfema-data-page/nfip-redacted-claims-v3) | 552,616 distinct downloaded records across bounded event windows |
| FEMA National Risk Index | [Official county service metadata](https://www.arcgis.com/home/item.html?id=39485e8035d446a5bff03259508ae355) | 3,232 rows, December 2025 context |

The claims API is `https://www.fema.gov/api/open/v3/NfipClaims`. The earlier v2 endpoint returned 404. Of the distinct downloaded claims, 53,853 are unmatched and 1,239 ambiguous under this rule. There are 69,632 records with a missing or negative payment field. Negative adjustments are preserved; missing values are not silently labelled as complete payments.

`BUILDVALUE` in NRI is building stock value, not an NFIP insured exposure denominator. `HRCN_EALT` is annual hurricane risk context, not the selected storm loss. Map attribution belongs to CARTO and OpenStreetMap. The MIT license covers project code; upstream data retain their source terms and attribution.

## Portfolio and AI boundaries

Portfolio CSV files require exactly `county_fips` and `insured_value`. Values must be finite and nonnegative, and county codes must be five digits and present in the county source. Duplicate county rows are summed. Uploads are limited to 2 MB. The app does not save uploads to disk. On a hosted app, upload processing occurs on its server.

Portfolio value within the corridor is a geographic screen. It is not predicted damage and cannot be obtained by scaling county claims without an appropriate exposure denominator.

The optional Nemotron agent uses a validated JSON tool plan. Python runs tools bound to the selected storm and renders all numerical evidence. Generated prose must use the required qualitative fields and cannot contain numerical quantities or URLs. Rejected prose is sent back to the model with the exact reason, for up to three attempts in total; if all fail, no AI text is shown. These checks do not prove semantic accuracy. A live Helene briefing from `nvidia/nemotron-3-super-120b-a12b` passed them on October 27, 2026. The agent does not rely on native function calling, and replies that wrap JSON in reasoning tags or code fences are unwrapped before validation.

The default summary is explicitly produced by Python. It is never presented as an AI response. Optional Tavily queries use the selected storm name and year and return links only from official NHC, FEMA, or weather.gov domains. Only if the user opts in are aggregate portfolio totals included in a Nebius request. Individual portfolio rows are not sent to Nebius. To protect API credits, each visit is limited to three AI briefings and three source lookups, and the whole app has a daily cap set by `DAILY_AI_LIMIT` (default 100). A briefing without portfolio data is reused for the same storm.

## Reproduce and test

Run from the repository root:

```sh
.venv/bin/python -m pytest -q
.venv/bin/python -m pip check
.venv/bin/python -m analysis.validation
```

To refresh sources and rebuild the study, which requires internet access and may take time:

```sh
.venv/bin/python -m scripts.fetch_sources
.venv/bin/python -u -m scripts.build_dataset
.venv/bin/python -m analysis.validation
```

The downloader uses ID pagination, checks counts, retries temporary errors, and resumes partial downloads. Raw claim caches and intermediate work are ignored by Git. API revisions can change a future snapshot; manifests identify this one. The included aggregate table can reproduce the benchmark without downloading raw claims.

Tests cover source parsing, geometry, duration units, ambiguous matching, missing payments, upload validation, agent restrictions, model independence from test targets, and dashboard interactions. GitHub Actions is configured but has not yet been run remotely. Only load the included trusted model artifact; joblib is not a format for untrusted uploads.

## Project map

`app.py` is the interface. `src/stormsight` contains data, geographic features, models, portfolios, and service adapters. `scripts` builds source snapshots. `analysis` rebuilds the benchmark. `tests` verifies behavior. `docs` holds the setup guide, architecture, submission draft, and video script. `PROJECT_HANDOFF.md` records current progress and exact next steps.

All current dependencies are pinned in `requirements.txt`. Use GitHub Desktop for commits. `.env`, Streamlit secrets, the virtual environment, raw claim caches, and temporary work must remain uncommitted.
