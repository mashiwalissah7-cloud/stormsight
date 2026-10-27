"""Exercise the shipped dashboard with its real, local benchmark artifacts."""
from streamlit.testing.v1 import AppTest
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / 'app.py'


def select(app, label):
    return next(widget for widget in app.selectbox if widget.label == label)


def test_dashboard_storm_switching_and_validation():
    app = AppTest.from_file(APP, default_timeout=60).run()
    assert not app.exception
    assert [tab.label for tab in app.tabs] == ['Storm briefing', 'Portfolio', 'Does it work?']
    assert any(m.label == 'Held out storms' and m.value == '5' for m in app.metric)
    assert next(b for b in app.button if b.label == 'Generate Nemotron briefing').disabled
    select(app, 'Storm').set_value('AL142024').run()
    assert not app.exception
    select(app, 'Compare observed and estimated').set_value('claim_count').run()
    assert not app.exception
    select(app, 'Historical season').set_value(2025).run()
    assert not app.exception


def test_removed_portfolio_cannot_be_sent_as_stale_evidence():
    app = AppTest.from_file(APP, default_timeout=60).run()
    assert app.session_state['portfolio-AL092024']['fictional_sample']
    next(c for c in app.checkbox if c.label == 'Use fictional sample portfolio').uncheck().run()
    assert not app.exception
    assert 'portfolio-AL092024' not in app.session_state.filtered_state
