# StormSight project handoff

Updated October 27, 2026, America/New_York. Update this file after each major task and include it in meaningful Git commits. It records actual state, not completion claims.

## Goal and hackathon requirements

Build StormSight for Mashiwal Issah's solo Nebius x NVIDIA Global AI Hackathon entry. Deadline shown in Devpost: October 30, 2026 at 1 PM EDT. Track: Best Apps and Agents. Required: working NVIDIA Nemotron inference on Nebius Token Factory, public code with MIT license and setup README, accessible demo, project description, public YouTube demonstration under three minutes, honest feedback on tools used. Verify final rules: https://nebiusglobalaihackathon.devpost.com/rules

Use Python and Streamlit with NOAA historical hurricane tracks, OpenFEMA NFIP claims, Census county geography, and FEMA NRI context. Evaluate county claims/payment estimates on unseen storms. Optional Tavily source lookup and a bounded Nemotron agent explain Python evidence. Never invent data, metrics, model IDs, API URLs, or successful integrations.

The user now wants autonomous development until human input is truly needed. Do not pause after every small step. Use GitHub Desktop for version control, not command line Git. README, Devpost, and video text should be plain professional English without contractions or dash punctuation. Do not restart the project. Preserve completed downloads.

## Location and runtime

Repository: /Users/ovabilli/Documents/GitHub/stormsight
GitHub user: mashiwalissah7-cloud
Branch: main. Local only at this update. Known commits: af475b9 Initial commit; 958e027 Add initial StormSight interface; fe413fe Build audited NFIP benchmark and evidence dashboard.
Python 3.14.6, virtual environment .venv. VS Code has this folder open.
Local app: http://127.0.0.1:8501/ ; original server exec session 60887.
The earlier ProofPlan site is abandoned and unrelated. Do not resume it.

## Completed and working

1. Repository created using GitHub Desktop, with MIT license and Python ignore rules. Initial interface committed.
2. NOAA file hurdat2-1851-2025-092326.txt downloaded unchanged and parsed: 55,524 observations, 1,988 storms. Helene and Milton maps and values verified in browser.
3. Census 2025 county file downloaded: 3,222 rows. County internal points drive the corridor calculation.
4. Official FEMA NRI owner FEMA_NationalRiskIndex verified, version December 2025 1.20.0. All 3,232 rows downloaded and checked against API count. NRI is context only, excluded from model predictors.
5. Geographic distance, hourly interpolation, nearby duration, ambiguity aware claim matching, and strict portfolio CSV handling implemented.
6. Redesigned Streamlit app has historical track map, county corridor, portfolio sample/upload, source ledger, optional API controls, and validation views that activate when artifacts exist.
7. Optional Nemotron JSON plan/execute agent implemented with a tool allowlist and numerical prose checks. Python renders numerical tables. Optional aggregate portfolio sharing requires a UI opt in. No live Nebius call has been tested.
8. Tavily adapter restricts returned URLs to official domains. No live Tavily call has been tested.
9. Latest test run: 23 passed. Covers parsing, coordinates, time units, date line interpolation, ambiguous matches, upload validation, agent checks, and invariance when final test targets are changed. Streamlit AppTest passed before model artifacts existed.
10. Source manifests, setup guide, architecture, and demo script drafted. CI workflow created but not run on GitHub.

## Currently being worked on

Claims ingestion and the corrected benchmark are complete. Current work: final artifact checks, README with actual results, browser review, and Git checkpoints through GitHub Desktop.

All 16 downloads completed after reducing the page size to 2,000. Raw and partial caches remain for reproducibility. No download is currently blocked.

## Unfinished

1. Final scientific and UI review of the completed artifacts. study_counties.csv, claims_audit.json, and claims_manifest.json now exist.
2. model.joblib, validation.json, test_predictions.csv, and test_storm_totals.csv now exist. Document their limitations and final figures, not the discarded preliminary complete case benchmark.
3. Final tests and browser review with model artifacts, README with actual results, Devpost draft, and Git checkpoint.
4. Public GitHub publication and Streamlit Cloud deployment.
5. Nebius account activation, credits, exact NVIDIA model ID and endpoint, private API key, and a successful live call. User is unsure whether activated. Builder Program application was pending review; Token Factory had reached billing. Do not enter payment details or ask for keys in chat.
6. Tavily account/key and live verification.
7. Public YouTube demo and final Devpost submission. Devpost draft exists, not submitted.
8. Calibrated property/portfolio loss prediction is not implemented. Portfolio reports value in the corridor only. Do not invent damage ratios.

## Important files

app.py: interface, maps, source evidence, portfolio and validation views.
src/stormsight/data.py: NOAA parser and exact source URL.
src/stormsight/features.py: haversine, hourly interpolation, county features, claim matching.
src/stormsight/model.py: fixed splits, mean baseline, Poisson gradient boosting, residual intervals, metrics.
src/stormsight/portfolio.py: strict CSV parsing and corridor value calculation.
src/stormsight/agent.py: optional Nebius planner, bounded tools, schema and numerical checks.
src/stormsight/news.py: optional official source lookup through Tavily.
scripts/fetch_sources.py: reproducible NOAA, Census, NRI downloads and manifests.
scripts/build_dataset.py: bounded FEMA columns/date windows, ID pagination, two download workers, aggregation.
analysis/validation.py: train and export actual benchmark.
tests/: pytest suite, including unittest compatible parser tests.
data/raw/: original sources and ignored raw claim caches.
data/processed/: county tables, source manifest, all county windows, future benchmark artifacts.
work/: ignored logs, temporary API metadata, partial downloads. Preserve for resume.
docs/SETUP.md, ARCHITECTURE.md, DEMO_SCRIPT.md: drafts.
.env.example: empty secrets template. Never commit .env or .streamlit/secrets.toml.
.streamlit/config.toml: theme and upload size.
.github/workflows/tests.yml: Python 3.14 tests.
requirements.txt: pinned installed direct dependencies.

## Dependencies and commands

Direct dependencies: streamlit 1.66.1, pandas 3.1.0, numpy 2.5.4, pydeck 0.9.3, scikit-learn 1.9.1, pytest 9.1.1, python-dotenv 1.2.4, openai 3.39.0, tavily-python 0.8.5, requests 2.34.2, joblib 1.6.0.

From the repository root:

```sh
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false
.venv/bin/python -m pytest -q
.venv/bin/python -m scripts.fetch_sources
.venv/bin/python -u -m scripts.build_dataset
.venv/bin/python -m analysis.validation
.venv/bin/python -m pip check
```

Use GitHub Desktop for commits. Do not use Git CLI.

## Scientific boundaries

Targets are matched NFIP claim records and gross building, contents, and increased cost of compliance payments, not total hurricane damage. Match county internal points within 250 km of the interpolated observed track, then dates from first proximity through three days after last proximity. Exclude ambiguous matches and affected county targets. The payment target sums available reported components and retains signed adjustments. Missing components are counted explicitly. Entirely missing targets and negative county sums are excluded. It is not complete or ultimate loss.

Train: Irene 2011, Isaac/Sandy 2012, Matthew 2016, Harvey/Irma 2017, Florence/Michael 2018.
Calibration: Dorian 2019, Laura/Sally 2020.
Final test: Ida 2021, Ian 2022, Idalia 2023, Helene/Milton 2024.

No rainfall, surge, coastal classification, or historical policy denominator. Current NRI is context only. 2025 geography is used retrospectively. Full observed tracks make this a retrospective benchmark, not forecast validation. Features: distance, nearby wind, duration, log land area, water fraction, latitude, longitude. Ranges use calibration residuals and have no guaranteed coverage.

## Errors and issues

FimaNfipClaims v2 returned 404. FEMA DataSets metadata verifies the replacement https://www.fema.gov/api/open/v3/NfipClaims . Do not use the obsolete endpoint.
FEMA intermittently returns 503. Downloader retries and resumes with ID cursors. Complete caches: data/raw/claims-STORM.json; partial caches: work/download-STORM.json. Counts and unique IDs are checked. Helene completed successfully with smaller pages.
A pandas datetime unit bug in duration was fixed and tested before training. A harmless joblib physical CPU detection warning falls back to logical cores.
Live APIs, cloud compatibility, hosting, and final submission remain unverified. Final UI review with model artifacts is pending.

## Exact next steps for another assistant

1. Audit process 89220 completed successfully: 23 tests passed. Inspect work/validation-run.log if details are needed.
2. Reconcile example county aggregates against cached raw records and verify artifact integrity.
3. Preserve the fixed model and split. Corrected held out county payment MAE is about $7.52 million versus $12.70 million for the mean baseline; payment range coverage is about 89.12%. Count MAE is about 87.23 versus 165.12. Large event totals are severely underestimated. Do not call these estimates operationally reliable.
4. Run Streamlit AppTest and browser checks with completed artifacts, including missing credentials, portfolio uploads, storm switching and every tab.
5. Rewrite README/submission text with verified behavior and actual metrics. Update this file after each major task.
6. Review Changes in GitHub Desktop for secrets/raw caches, then commit. Publish reviewed source and public aggregates if account access permits.
7. Stop only for necessary user involvement with Nebius/keys or new cloud authentication, legal terms, or security permissions. Provide one clear next action.

## Major task update: ingestion completed, target audit correction

All 16 event windows downloaded, 552,616 distinct claim records. Initial strict complete case benchmark was generated, but the audit found severe selection bias: any missing field excluded an entire county, including many severely affected counties. Those preliminary metrics must not be used. The target definition is being corrected to sum available reported payment components, retain signed adjustments, and explicitly track missing components. It is not a complete or ultimate loss target. Ambiguous targets, negative county sums, and entirely missing payment targets remain excluded. The fixed model/splits are unchanged. Rebuild from cached raw records, rerun validation, and document final metrics and missingness. No data downloads need restarting.

## Major task update: corrected benchmark completed

552,616 distinct downloaded claims; 6,460 study county rows; 6,299 eligible targets. 53,853 records unmatched and 1,239 ambiguous under the matching rule. There are 69,632 downloaded records with missing or negative payment fields; negative signed adjustments are retained in the reported sum, while missing fields remain unestimated. The model uses 3,322 training rows, 1,047 calibration rows, and 1,930 final test rows. Gradient boosting was selected for both targets using calibration MAE. The model severely underestimates Ian, Helene, Milton, and Ida totals, and the UI now warns prominently. No final test tuning was performed. The initial target definition was corrected because an audit exposed exclusion bias; preliminary results are superseded.

## Checkpoint: source and benchmark verification

All 23 tests passed after the corrected target aggregation rebuild. No failed tests remain. The joblib CPU detection warning is nonfatal. Credential scan found no private .env or secrets.toml files; the template contains empty values. Raw claims and partial downloads remain ignored. Preparing the first meaningful data/model/agent checkpoint through GitHub Desktop. README and final app verification are the next task.

## Major task update: first checkpoint and UI audit

Checkpoint fe413fe saved through GitHub Desktop, 40 files, clean working tree verified before further changes. AppTest initially loaded all tabs without an app exception. The ad hoc storm switching script failed because it selected the season widget by the wrong index, not because the app failed. Replacing that check with label based widget selection. Fixed stale portfolio totals by processing and clearing portfolio state before the agent reads it. Added automatic work directory creation for downloads on a fresh clone. These fixes need regression checks and the next checkpoint.

## Major task update: independent audit and documentation review, October 27

Continued by Claude from the state above. Nothing was rebuilt and no data or model artifact was changed.

Verified in an independent environment: all 23 non interface tests pass, and app.py compiles. tests/test_app.py (Streamlit AppTest) was not run there because Streamlit is not installed in that environment. It must be run on the Mac with `.venv/bin/python -m pytest -q`; expected result is 25 passed.

Reviewed the portfolio fix: the portfolio block now runs before the briefing block, clears `portfolio-{sid}` first, and only stores totals for a valid current upload or the fictional sample. The work, raw, and processed directories are created at the start of `scripts/build_dataset.py`. Both fixes look correct and are covered by the new AppTest file.

Checked every figure in README.md and docs/DEVPOST_DRAFT.md against validation.json, claims_audit.json, test_storm_totals.csv, and the raw files: HURDAT2 has 1,988 storms and 55,524 observations; the Gazetteer has 3,222 counties; NRI has 3,232 rows. All metrics, coverage values, split sizes, and the Helene and Ian totals match.

Edits made:
1. app.py: replaced the en dash in the source caption with "1851 through 2025".
2. docs/DEVPOST_DRAFT.md: project name changed to "StormSight: An AI Evidence Agent for Hurricane Flood Claims" because the model estimates matched NFIP claims and reported payments, not total hurricane losses. Corrected "scikit-learn". Added the claim count result and measured coverage to Accomplishments.
3. docs/DEMO_SCRIPT.md: "flood insurance losses" changed to "flood insurance claims" for the same reason.

Streamlit Community Cloud now defaults to Python 3.14, so the pinned requirements should match the local environment. Select Python 3.14 in the deploy dialog under Advanced settings if it is offered.

Files that must be included in the next GitHub Desktop commit: tests/test_app.py, docs/DEVPOST_DRAFT.md, docs/START_HERE.md, data/processed/artifact_audit.json, plus the modified README.md, app.py, scripts/build_dataset.py, docs/DEMO_SCRIPT.md, and this file. Confirm that no .env, .streamlit/secrets.toml, data/raw/claims files, or work files appear in Changes.

Remaining steps, in order, before October 30, 2026 at 1 PM EDT:
1. Run the full test suite on the Mac and confirm 25 passed.
2. Commit through GitHub Desktop and publish the repository as public.
3. Nebius: the user activates Token Factory, confirms credits, copies the exact Nemotron model ID and endpoint, and puts the key in .env himself. Never paste keys into chat or commit them. Then run one live briefing and record what happened.
4. Tavily: same process for the optional key, then one live lookup.
5. Deploy on Streamlit Community Cloud with the keys in the app Secrets panel, not in the repository.
6. Record the YouTube video under three minutes from docs/DEMO_SCRIPT.md and set it to public, as the rules require.
7. Fill the Devpost fields with the real URLs, model ID, and honest Nebius feedback, then submit.

Checkpoint 318b13f saved through GitHub Desktop on October 27: all 9 reviewed files committed, working tree clean, no keys or private files in any commit. The repository is not yet published to GitHub; the user is deciding on public visibility. The full suite, including tests/test_app.py, still needs one run on the Mac or through GitHub Actions after publishing.

Agent hardening, October 27: Nemotron 3 Super is a reasoning model, so `generate_briefing` now extracts the JSON object from each reply (ignoring think tags and code fences), allows 4,096 output tokens, and waits up to 90 seconds. Added a test for the extractor; 24 non interface tests pass, so the full suite should report 26 passed on the Mac. Created a private, Git ignored `.env` with NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1/ (shown in the user's Token Factory dashboard) and NEBIUS_MODEL=nvidia/nemotron-3-super-120b-a12b (published by Nebius; confirm it in the model catalog). The user must paste NEBIUS_API_KEY himself. No live call has been made yet.

Usage limits, October 27: the hosted app now allows three Nemotron briefings and three Tavily lookups per visit, with an app wide daily cap from DAILY_AI_LIMIT (default 100). A portfolio free briefing is reused for the same storm and labelled as reused. The sidebar shows the configured model ID. tests/test_app.py now clears the Nebius and Tavily variables so a private .env cannot change the result.


Live verification, October 27 at about 12:10 PM EDT: the user saved his own Nebius key in `.env`. The full suite reported 25 passed and 1 failed; the failure was `app.session_state.filtered_state`, which Streamlit 1.66 AppTest no longer exposes, so the test now uses `in app.session_state`. The app started locally and a Helene briefing from `nvidia/nemotron-3-super-120b-a12b` returned with all prose checks passing. The Nebius account has the $25 Builder Program credit applied. Remaining: commit, publish, Streamlit Cloud deployment, optional Tavily key, video, Devpost.

Published and deployed, October 27: commit f487aa7 is public at https://github.com/mashiwalissah7-cloud/stormsight and GitHub Actions passed (Check StormSight #1). Streamlit Community Cloud serves https://stormsight-hurricane.streamlit.app/ on Python 3.14 with secrets set by the user. A signed out browser loaded every tab and a hosted Helene briefing passed all prose checks. The Nebius key was shown in chat screenshots, so the user should delete the two old keys, create a fresh one, and update both `.env` and the Streamlit Secrets before submission. Remaining: key rotation, commit these doc updates, video, Devpost.

Presentation audit, October 27 (user's launch checklist, without changing anything the hackathon requires): no purple gradients, fake reviews, fake metrics, photos, cursor or scroll animations, or customer counters were present. Changes: the 🌀 emoji favicon and sidebar icon were replaced by `assets/favicon.png` (a drawn storm track in the app's map colors); the pill shaped badge now has square corners; the hero now says what the app does ("Hurricane flood claims, county by county"); the validation heading is now "How accurate is the model?"; `pages/privacy.py` and `pages/terms.py` were added and linked from a footer on every tab; `client.showSidebarNavigation = false` hides the automatic page menu; `tests/test_pages.py` checks both pages (28 tests in total). Not done: a custom domain, because Streamlit Community Cloud only offers custom `.streamlit.app` subdomains, and Streamlit's own hosting badge and toolbar, which Community Cloud controls. There is no "Made with AI" tag in the app.
