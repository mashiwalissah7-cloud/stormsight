"""Terms and conditions for the public StormSight app."""
from pathlib import Path
import streamlit as st

ICON = Path(__file__).resolve().parents[1] / 'assets' / 'favicon.png'
st.set_page_config(page_title='Terms and conditions | StormSight', page_icon=str(ICON), layout='centered')
st.page_link('app.py', label='Back to StormSight')
st.title('Terms and conditions')
st.caption('Effective October 27, 2026')
st.markdown('''
By using StormSight, you agree to these terms. If you do not agree, please do not use the app.

**Research and education only.** StormSight is a research prototype. It is not a weather forecast, an emergency warning service, an insurance quote, a catastrophe model, or financial, legal, or engineering advice. For current hazards, follow the National Hurricane Center and your local emergency officials.

**Estimates can be wrong.** Model estimates and ranges come from a small historical benchmark and badly underestimate some large storms. AI briefings are written by a language model and can contain errors even after automated checks. Verify anything important against the original sources.

**Your uploads.** You are responsible for any file you upload and must have the right to use it. Do not upload personal, confidential, or regulated data.

**Fair use.** Do not try to overload the app, get around its usage limits, or send automated requests. AI features may be limited or turned off at any time.

**Data and code.** Public data come from NOAA, FEMA, and the U.S. Census Bureau and remain subject to their terms. Map data belong to CARTO and OpenStreetMap contributors. The StormSight source code is released under the MIT license.

**No warranty.** The app is provided as is, without warranties of any kind. To the extent allowed by law, the author is not liable for any loss arising from its use.

**Changes and contact.** These terms may be updated, and the effective date above will change when they are. Questions can be raised as an issue on the [StormSight GitHub repository](https://github.com/mashiwalissah7-cloud/stormsight/issues).
''')
