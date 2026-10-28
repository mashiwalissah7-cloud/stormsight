# Devpost submission text

Final copy for the Devpost form. Every figure comes from `data/processed` and was checked on October 27, 2026. Paste each section into the matching field.

## Project name

StormSight: An AI Evidence Agent for Hurricane Flood Claims

## Elevator pitch

An AI agent that turns NOAA hurricane tracks and FEMA flood claims into a county briefing, then shows exactly where its model succeeds and where it fails.

## Inspiration

After a hurricane, the first two questions are where it went and what the flooding cost. Storm maps answer the first question well. The second is harder, because flood insurance claims sit in large public datasets that are easy to misread. I built StormSight to connect the two while keeping every assumption visible, so a student or researcher can see what the evidence supports and what it does not.

## What it does

Pick a historical Atlantic hurricane. StormSight draws the observed NOAA track, finds every county whose center lies within 250 km of it, and estimates flood insurance (NFIP) claim counts and reported payments for each county with an empirical range. For storms in the study, observed FEMA claims sit next to the estimates.

The NVIDIA Nemotron 3 Super agent, running on Nebius Token Factory, plans which evidence tools to call. Python runs those tools and renders every number. Nemotron then writes the briefing: a summary, the key uncertainties, and what to watch. If the model writes any number or link, the briefing is rejected, so the AI cannot invent figures.

A Portfolio tab screens insured value inside the storm corridor. A Does it work? tab shows the benchmark, how often the ranges held, and the largest misses.

## How I built it

Python, Streamlit, pandas, scikit-learn, and pydeck. The data comes from NOAA HURDAT2 (1,988 storms and 55,524 observations), OpenFEMA NFIP claims v3 (552,616 claim records), the 2025 Census county Gazetteer, and the FEMA National Risk Index for context.

Sixteen storms from 2011 through 2024 were split before any fitting: eight for training, three for calibration, and five held out for the final test. Poisson gradient boosting is compared with a mean baseline and selected on calibration error. Ranges come from the 90th percentile of calibration errors.

The agent uses a JSON tool plan checked against an allowlist. Tools are bound to the selected storm, so the model cannot choose files, URLs, or code. Replies are unwrapped from reasoning text before validation. The public app limits AI calls per visit and per day to protect credits. Twenty nine automated tests run on every push through GitHub Actions.

## Challenges I ran into

The FEMA claims endpoint I first used had been retired, so I moved to v3 and wrote a downloader with smaller pages, retries, count checks, and resumable cursors. My first target definition dropped any county with a missing payment field. An audit showed that this removed many of the hardest hit counties, so I replaced it with a target that sums the available payment components and reports what is missing.

The hardest result to accept was the model itself: it badly underestimates the largest storms. Helene paid about $6.24 billion in matched claims, and the model estimated about $200.6 million. I chose to show that failure in the app rather than hide it behind an average score.

## Accomplishments that I am proud of

On five storms the model never saw, average county payment error fell from $12.70 million to $7.52 million, and claim count error fell from 165.12 to 87.23 records, compared with the baseline. The ranges covered 89.12% of observed payments and 87.77% of claim counts. The Nemotron agent runs live on a public app, and every number a visitor sees comes from code, not from the language model.

## What I learned

A storm track is not a flood footprint. A sum of reported payments is not total damage. Matching dates and counties does not prove that a storm caused a claim. A research tool earns trust by showing those limits as clearly as its results.

## What is next for StormSight

Add rainfall and storm surge, use NFIP policy counts as an exposure measure, expand the storm set, and test the model on forecast tracks instead of observed ones.

## Built with

python, streamlit, pandas, numpy, scikit-learn, pydeck, nvidia-nemotron, nebius-token-factory, noaa-hurdat2, openfema, github-actions

## Links

1. Live app: https://stormsight-hurricane.streamlit.app/
2. Code: https://github.com/mashiwalissah7-cloud/stormsight
3. Video: https://youtu.be/GSQdjodEvrk

## Model and track

Model: `nvidia/nemotron-3-super-120b-a12b` on Nebius Token Factory, verified live on October 27, 2026. Track: Best Apps and Agents.

## Nebius feedback (edit to match your own experience)

The Builder Program welcome email and the $25 Token Factory promo code arrived within minutes of applying. Billing setup asks for a card even when the account is funded by promotional credit, which was unexpected for a student account. The model catalog shows display names but not the exact API model ID, so I found the ID in a Nebius blog post. The OpenAI compatible endpoint worked on the first call with the standard Python client. Nemotron 3 Super followed a strict JSON only instruction and a no numbers rule, and its briefings passed my validation both locally and on the hosted app.
