import pytest
from sparkprivacy.scanner import scan_text, redact_text, luhn_valid, MAX_SCAN_CHARS
from sparkprivacy.policy import decide, validate_actions, DEFAULT_ACTIONS


def test_email_redaction():
    d=decide('Write to jane@example.com immediately')
    assert d.disposition=='redacted'
    assert '[REDACTED:EMAIL]' in d.sanitized
    assert 'jane@example.com' not in d.sanitized


def test_api_key_blocked_without_original():
    d=decide('secret sk-'+'a'*28)
    assert d.disposition=='blocked' and d.sanitized is None
    assert d.categories=={'api_key':1}


def test_credit_card_luhn():
    assert luhn_valid('4111 1111 1111 1111')
    assert not luhn_valid('4111 1111 1111 1112')
    assert 'payment_card' in [f.category for f in scan_text('Test card 4111 1111 1111 1111')]
    assert 'payment_card' not in [f.category for f in scan_text('Test card 4111 1111 1111 1112')]


def test_no_false_card_on_simple_digits():
    assert not scan_text('0000000000000000')


def test_phone_category():
    assert any(x.category=='phone' for x in scan_text('Call +1 415-555-0132'))


def test_korean_rrn():
    assert any(x.category=='korean_rrn' for x in scan_text('900101-1234567'))


def test_ssn():
    assert any(x.category=='us_ssn' for x in scan_text('123-45-6789'))


def test_clean():
    d=decide('Summarize this harmless paragraph.')
    assert d.disposition=='allowed' and d.sanitized=='Summarize this harmless paragraph.'


def test_monitor_exposes_nonredacted_content_explicitly():
    actions=dict(DEFAULT_ACTIONS);actions['email']='monitor'
    d=decide('a@example.com',actions)
    assert d.disposition=='observed' and d.sanitized=='a@example.com'


def test_reject_unknown_actions():
    with pytest.raises(ValueError):validate_actions({'email':'skip'})


def test_reject_large_input():
    with pytest.raises(ValueError):scan_text('x'*(MAX_SCAN_CHARS+1))


def test_no_duplicate_overlap():
    s='+1 415-555-0132 and mail me at security@example.org'
    f=scan_text(s)
    assert all(a.end <= b.start for a,b in zip(f,f[1:]))
    assert 'security@example.org' not in redact_text(s,f)
