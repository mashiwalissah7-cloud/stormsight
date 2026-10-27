# Demonstration video script

Target length: about 2 minutes 40 seconds. YouTube or Vimeo, set to public or unlisted with no password. Only the first three minutes are reviewed.

Record on the live app: https://stormsight-hurricane.streamlit.app/ . On a Mac, press Shift + Cmd + 5, choose Record Entire Screen, open Options, pick the built in microphone, then click Record. Stop from the menu bar.

## 0:00 to 0:20, opening (Helene already on screen)

"This is StormSight. After a hurricane, a map shows where the storm went, but not what the flooding cost. StormSight connects NOAA storm tracks with FEMA flood insurance claims, and uses an NVIDIA Nemotron agent on Nebius to explain the evidence without inventing numbers."

## 0:20 to 1:00, storm briefing

Scroll slowly past the map and the county table.

"This is Hurricane Helene in 2024. The line is the observed track, and each dot is a county center within 250 kilometers. For every county, the model estimates flood insurance claims and payments, with a range. Helene was held out from training, so I can compare the estimates with what FEMA actually paid."

## 1:00 to 1:45, the agent

In the sidebar, choose Milton (2024). Scroll to Generate Nemotron briefing and click it. Keep talking while it runs.

"Now the agent. Nemotron, running on Nebius Token Factory, decides which evidence tools to call. Python runs those tools and renders every number on the page. Nemotron writes only the summary, the uncertainties, and what to watch. If it writes a number or a link, the briefing is rejected, so it cannot invent figures."

When it finishes, open Agent tool trace for two seconds.

## 1:45 to 2:05, portfolio

Open the Portfolio tab.

"The Portfolio tab screens insured value inside the storm corridor. It is a geographic screen, not a loss estimate."

## 2:05 to 2:35, does it work

Open the Does it work? tab and scroll to the storm totals.

"On five storms the model never saw, it cut average county payment error from 12.7 million dollars to 7.5 million compared with a simple baseline, and its ranges held about 89 percent of the time. But it badly underestimates the biggest storms. Helene paid about 6.2 billion dollars, and the model estimated about 200 million. StormSight shows that failure instead of hiding it."

## 2:35 to 2:45, close

"StormSight is open source and live at stormsight-hurricane.streamlit.app. Thank you."
