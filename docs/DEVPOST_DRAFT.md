# Devpost project draft

Status: local draft for review. Do not submit until the Nebius runtime call, hosted demo, repository, and public video are verified. Replace any remaining pending items with real evidence.

## Project name

StormSight: An AI Evidence Agent for Hurricane Flood Claims

## Suggested elevator pitch

Explore hurricane flood insurance evidence with NOAA tracks, FEMA claims, transparent county estimates, and an AI briefing designed to show its sources and limitations.

## Inspiration

A storm map can show where a hurricane travelled, but it cannot establish how much flooding cost. StormSight was created to connect those questions while making the assumptions visible. Its audience is students and researchers who need an understandable way to inspect hurricane flood insurance evidence.

## What it does

StormSight maps historical NOAA observations, matches FEMA flood claims to county and date windows, estimates county claim counts and reported payments, and compares those estimates with observed data. A portfolio screen calculates insured value near the storm path. A separate validation view reveals baseline results, empirical ranges, and the largest model failures.

The application includes an optional NVIDIA Nemotron evidence agent for Nebius Token Factory. It selects bounded evidence tools and writes qualitative explanations. Python computes and displays the numbers. The local summary is clearly labelled as Python output when the AI service is disconnected.

## How it was built

The project uses Python, Streamlit, pandas, NumPy, scikit-learn, and pydeck. Public sources include NOAA HURDAT2, OpenFEMA NFIP v3, Census county geography, and FEMA National Risk Index context. Sixteen selected storms are divided into training, calibration, and final test groups. A mean baseline is compared with Poisson gradient boosting. Model selection uses calibration error.

The agent adapter uses a JSON plan with an allowed set of Python tools. It rejects generated numerical quantities and unverified links in prose. Optional Tavily lookup restricts returned links to official sources. These controls reduce specific errors but do not prove that every generated explanation is correct.

## Challenges

The earlier FEMA claims endpoint had been replaced. Large API requests intermittently failed, so the downloader uses smaller pages, retries, count checks, and resumable cursors. Missing payment fields required careful auditing. The initial complete case target removed important affected counties; the corrected target sums available reported components and exposes missingness.

The model also substantially underestimates large event totals. This is shown directly in the product instead of being hidden by an average score.

## Accomplishments

The working local prototype joins public evidence with reproducible calculations and an honest evaluation. The final test includes five storms and 1,930 eligible county rows. Payment mean absolute error is about $7.52 million compared with $12.70 million for the mean baseline. Claim count mean absolute error is 87.23 records compared with 165.12. Measured range coverage is 89.12% for payments and 87.77% for counts. This improvement does not make the model operationally reliable: Helene and Ian totals are still severely underestimated.

## What was learned

Track proximity is not a flood footprint. An incomplete reported payment sum is not ultimate loss. Matching dates and counties does not prove storm causation. A useful research tool needs to expose those boundaries as clearly as it displays its estimates.

## What is next

Add rainfall and surge evidence, historical policy exposure, and a broader storm cohort. Improve event level validation before using estimates for decisions. Validate the live agent integration and public deployment before presenting the hackathon entry as complete.

## Built with

Python, Streamlit, pandas, NumPy, scikit-learn, pydeck, NOAA HURDAT2, OpenFEMA, Census Gazetteer, FEMA NRI. Add Nebius Token Factory, NVIDIA Nemotron, and Tavily as functioning integrations only after recording successful runtime calls.

## Remaining submission fields

1. Public repository URL: pending publication.
2. Hosted application URL: pending deployment.
3. Public YouTube video URL: pending recording, under three minutes.
4. Exact NVIDIA model identifier: pending dashboard verification.
5. Nebius feedback: record actual onboarding and runtime observations after the live test. Do not invent speed, quality, or cost comparisons.
6. Track: Best Apps and Agents.

Official requirements: https://nebiusglobalaihackathon.devpost.com/rules
