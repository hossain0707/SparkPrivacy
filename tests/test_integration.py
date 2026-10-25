import pytest
from fastapi.testclient import TestClient
import sparkprivacy.server as server

@pytest.fixture
def app_client(tmp_path,monkeypatch):
    captured=[]
    async def fake_forward(payload,endpoint,upstream_key):
        captured.append(payload)
        return {'id':'cmpl-1','choices':[{'index':0,'finish_reason':'stop','message':{'role':'assistant','content':'Please email support@example.com'}}]}
    monkeypatch.setattr(server,'forward',fake_forward)
    app=server.create_app(tmp_path,testing=True)
    with TestClient(app) as client:
        client.headers['X-SparkPrivacy-Token']=app.state.token
        client.post('/api/gateway/config',json={'endpoint':'http://127.0.0.1:8000/v1/chat/completions','model':'mock-local'})
        yield client,captured
    app.state.store.close()


def test_request_and_response_have_redactions(app_client):
    client,captured=app_client
    response=client.post('/api/gateway/test',json={'prompt':'Contact jane@example.com for details'})
    assert response.status_code==200
    assert 'jane@example.com' not in str(captured)
    assert '[REDACTED:EMAIL]' in captured[0]['messages'][0]['content']
    assert response.json()['choices'][0]['message']['content']=='Please email [REDACTED:EMAIL]'
    audit=client.get('/api/audit').json()['events']
    assert len(audit)==2
    assert 'jane@example.com' not in str(audit)


def test_detected_secret_never_forwards(app_client):
    client,captured=app_client
    response=client.post('/api/gateway/test',json={'prompt':'My key is ghp_'+('a'*26)})
    assert response.status_code==403
    assert captured==[]


def test_gateway_requires_session_authentication(app_client):
    client,captured=app_client
    response=client.post('/v1/chat/completions',headers={'X-SparkPrivacy-Token':''},json={'model':'mock','messages':[{'role':'user','content':'hi'}]})
    assert response.status_code==401


def test_ai_gateway_response_does_not_include_extra_model_fields(app_client):
    client,captured=app_client
    result=client.post('/api/gateway/test',json={'prompt':'Hello'}).json()
    assert set(result)=={'id','choices'}
