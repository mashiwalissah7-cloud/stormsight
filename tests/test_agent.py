import pytest
from src.stormsight.agent import validate_numbers,validate_plan,validate_narrative,generate_briefing

def test_numbers_reject_invention():
    assert validate_numbers('Total 120',{'total':120})=='Total 120'
    with pytest.raises(ValueError): validate_numbers('Total 999',{'total':120})
    with pytest.raises(ValueError): validate_numbers('two million',{'total':120})

def test_plan_cannot_execute_arbitrary_tools():
    with pytest.raises(ValueError): validate_plan('{"tools":["run_shell"]}',{'get_storm_track'})
    assert validate_plan('{"tools":["get_storm_track"]}',{'get_storm_track'})==['get_storm_track']

def test_prose_cannot_override_evidence_numbers():
    with pytest.raises(ValueError): validate_narrative('{"summary":"120 losses","uncertainties":"x","watch_next":"y"}',{'n':120})
    with pytest.raises(ValueError): validate_narrative('{"summary":"See https://evil.test","uncertainties":"x","watch_next":"y"}',{})

def test_missing_config_never_calls_network():
    with pytest.raises(ValueError,match='Set the Nebius'):
        generate_briefing({}, {})


def test_extract_json_ignores_reasoning_and_fences():
    from src.stormsight.agent import extract_json
    assert extract_json('{"tools": ["list_storms"]}') == '{"tools": ["list_storms"]}'
    assert extract_json('<think>pick tools</think>\n```json\n{"tools": []}\n```') == '{"tools": []}'
    assert extract_json('reasoning only</think>{"a": "b"}') == '{"a": "b"}'
    with pytest.raises(ValueError):
        extract_json('no json here')


def test_rejected_prose_names_the_disallowed_tokens():
    from src.stormsight.agent import disallowed_tokens
    assert disallowed_tokens('Milton in 2024 was one of the storms, see www.example.com') == ['2024', 'one', 'www.example.com']
    assert disallowed_tokens('Estimates are proxies, not verified causation.') == []
    with pytest.raises(ValueError, match='2024'):
        validate_narrative('{"summary":"Milton in 2024","uncertainties":"x","watch_next":"y"}', {})
