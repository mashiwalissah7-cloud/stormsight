"""The legal pages load from the dashboard and link back to it."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / 'app.py'


def test_dashboard_links_to_legal_pages():
    app = AppTest.from_file(APP, default_timeout=60).run()
    assert not app.exception


def test_privacy_and_terms_pages_render():
    for page, heading in [('pages/privacy.py', 'Privacy policy'), ('pages/terms.py', 'Terms and conditions')]:
        app = AppTest.from_file(APP, default_timeout=60).run()
        app.switch_page(page).run()
        assert not app.exception
        assert app.title[0].value == heading
