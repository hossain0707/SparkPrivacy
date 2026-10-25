import pytest
from fastapi.testclient import TestClient
from sparkprivacy.server import create_app

@pytest.fixture
def client(tmp_path):
    app=create_app(tmp_path,testing=True)
    with TestClient(app) as c:
        c.headers.update({'X-SparkPrivacy-Token':app.state.token})
        yield c
    app.state.store.close();app.state.tunnels.close()


def test_health(client):
    r=client.get('/health')
    assert r.status_code==200 and r.json()['local_only'] is True


def test_html_embeds_secret_token(client):
    r=client.get('/')
    assert r.status_code==200 and '__SP_SESSION_TOKEN__' not in r.text
    assert client.app.state.token in r.text
    assert 'Data Inspector' in r.text


def test_unauthorized(client):
    r=client.get('/api/status',headers={'X-SparkPrivacy-Token':'incorrect'})
    assert r.status_code==401


def test_reject_host_header(client):
    r=client.get('/health',headers={'Host':'evil.attacker.com'})
    assert r.status_code==403


def test_reject_cross_origin(client):
    r=client.post('/api/inspect',headers={'Origin':'https://evil.example'},json={'text':'hello'})
    assert r.status_code==403


def test_scan_and_metadata_only(client):
    assert client.post('/api/inspect',json={'text':'safe content'}).json()['disposition']=='allowed'
    r=client.post('/api/inspect',json={'text':'user@example.com'})
    assert r.json()['disposition']=='redacted'
    events=client.get('/api/audit').json()['events']
    assert len(events)==2
    assert 'user@example.com' not in str(events)


def test_set_policy(client):
    policy=client.get('/api/policies').json()['actions']
    policy['email']='block'
    assert client.put('/api/policies',json={'actions':policy}).status_code==200
    r=client.post('/api/inspect',json={'text':'user@example.org'}).json()
    assert r['disposition']=='blocked'
    assert r['sanitized'] is None


def test_invalid_policy(client):
    assert client.put('/api/policies',json={'actions':{'email':'wrong'}}).status_code==422


def test_generate_pdf(client):
    r=client.get('/api/report.pdf')
    assert r.status_code==200 and r.content.startswith(b'%PDF')
    assert r.headers['content-type']=='application/pdf'


def test_purge(client):
    client.post('/api/inspect',json={'text':'person@example.com'})
    assert client.post('/api/audit/purge',json={'days':0}).json()['deleted']==1
    assert client.get('/api/audit').json()['stats']['total']==0


def test_config_rejects_nonloopback(client):
    r=client.post('/api/gateway/config',json={'endpoint':'http://evil.example:8000/v1/chat/completions','model':'x'})
    assert r.status_code==422


def test_local_api_requires_model(client):
    r=client.post('/api/gateway/test',json={'prompt':'hi'})
    assert r.status_code==409


def test_api_bearer_token(client):
    token=client.app.state.token
    r=client.post('/v1/chat/completions',headers={'Authorization':'Bearer wrong','X-SparkPrivacy-Token':''},json={})
    assert r.status_code==401
    r=client.post('/v1/chat/completions',headers={'Authorization':'Bearer '+token,'X-SparkPrivacy-Token':''},json={'model':'x','messages':[{'role':'user','content':'sk-'+'z'*30}]})
    assert r.status_code==403


def test_static_assets(client):
    for name in ('app.js','styles.css','mark.svg'):
        assert client.get('/static/'+name).status_code==200
    assert client.get('/static/../server.py').status_code==404


def test_payload_size_rejected(client):
    r=client.post('/api/inspect',content='x'*300000,headers={'Content-Type':'application/json'})
    assert r.status_code==413

def test_reject_fake_ipv6_host(client):
    r=client.get('/health',headers={'Host':'[evil.example]:8000'})
    assert r.status_code==403
