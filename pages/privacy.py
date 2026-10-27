"""Privacy policy for the public StormSight app."""
from pathlib import Path
import streamlit as st

ICON = Path(__file__).resolve().parents[1] / 'assets' / 'favicon.png'
st.set_page_config(page_title='Privacy policy | StormSight', page_icon=str(ICON), layout='centered')
st.page_link('app.py', label='Back to StormSight')
st.title('Privacy policy')
st.caption('Effective October 27, 2026')
st.markdown('''
StormSight is a free research and education app built by Mashiwal Issah. This page explains what happens to information when you use it.

**What StormSight does not collect.** There are no accounts, sign ups, contact forms, or advertising. StormSight does not ask for your name or email address and does not sell data.

**Portfolio uploads.** If you upload a portfolio CSV file, it is read in memory during your session to calculate totals. It is not saved to disk or to a database, and uploads are limited to 2 MB. The file should contain only county codes and values. Do not upload personal or confidential information.

**AI briefings.** When you click Generate Nemotron briefing, the app sends public storm and county evidence to Nebius Token Factory, which runs the NVIDIA Nemotron model. Portfolio totals are sent only if you tick the box that includes them, and individual portfolio rows are never sent. Nebius handles these requests under its own terms and privacy policy.

**Official source lookup.** When the Tavily lookup is available and you click it, the app sends only the storm name and year to Tavily.

**Hosting and maps.** The app is hosted on Streamlit Community Cloud, operated by Snowflake, which may record technical information such as IP addresses and browser details under its own privacy notice. Map tiles load from CARTO and OpenStreetMap servers, which receive standard web request information from your browser. StormSight's own code does not set tracking cookies.

**Usage limits.** To protect shared API credits, the app counts AI requests per browser session and per day. These counts are kept in memory and are not linked to your identity.

**Children.** StormSight is not directed to children under 13.

**Changes and contact.** This policy may change as the project changes, and the effective date above will be updated. Questions can be raised as an issue on the [StormSight GitHub repository](https://github.com/mashiwalissah7-cloud/stormsight/issues).
''')
