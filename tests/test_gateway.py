import pytest
from sparkprivacy.gateway import validate_endpoint, sanitize_request, sanitize_response
from sparkprivacy.policy import DEFAULT_ACTIONS

@pytest.mark.parametrize('url',[
    'https://example.com/v1/chat/completions','http://192.168.1.4:8000/v1/chat/completions',
    'http://169.254.169.254:80/v1/chat/completions','http://evil.com@127.0.0.1:8000/v1/chat/completions',
    'http://127.0.0.1:8000/metadata','http://127.0.0.1:8000/v1/chat/completions?token=x',
])
def test_ssrf_rejected(url):
    with pytest.raises(ValueError):validate_endpoint(url)


def test_loopback_urls_allowed():
    assert validate_endpoint('http://127.0.0.1:8000/v1/chat/completions')
    assert validate_endpoint('http://localhost:12345/v1/chat/completions')


def test_request_blocked_before_forward():
    payload={'model':'test','messages':[{'role':'user','content':'key sk-'+'b'*30}]}
    clean,reason=sanitize_request(payload,DEFAULT_ACTIONS)
    assert clean is None and reason['disposition']=='blocked'


def test_request_redacted_and_unknown_fields_dropped():
    payload={'model':'local','messages':[{'role':'user','content':'email me jane@example.org', 'secret_attachment':'DO NOT FORWARD'}],
             'tools':[{'confidential':'DO NOT FORWARD'}], 'stream':False}
    clean,reason=sanitize_request(payload,DEFAULT_ACTIONS)
    assert clean['messages']==[{'role':'user','content':'email me [REDACTED:EMAIL]'}]
    assert 'tools' not in clean
    assert reason['disposition']=='redacted'


def test_reject_streaming():
    with pytest.raises(ValueError,match='Streaming'):
        sanitize_request({'model':'local','stream':True,'messages':[{'role':'user','content':'hello'}]},DEFAULT_ACTIONS)


def test_reject_multimodal():
    with pytest.raises(ValueError,match='text'):
        sanitize_request({'model':'local','messages':[{'role':'user','content':[{'image':'somebase64'}]}]},DEFAULT_ACTIONS)


def test_response_redaction():
    raw={'choices':[{'message':{'role':'assistant','content':'send to person@example.com','hidden':'secret'},'logprobs':'secret'}], 'unsafe_metadata':'top'}
    secured,info=sanitize_response(raw,DEFAULT_ACTIONS)
    assert secured['choices'][0]['message']['content']=='send to [REDACTED:EMAIL]'
    assert 'hidden' not in str(secured) and 'logprobs' not in str(secured) and 'unsafe_metadata' not in str(secured)
    assert info['disposition']=='redacted'


def test_response_blocked_secret():
    raw={'choices':[{'message':{'role':'assistant','content':'sk-'+'c'*28}}]}
    secured,info=sanitize_response(raw,DEFAULT_ACTIONS)
    assert info['disposition']=='blocked'
    assert secured['choices'][0]['message']['content']=='[BLOCKED BY SPARKPRIVACY POLICY]'
