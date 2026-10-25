from sparkprivacy.store import Store
from sparkprivacy.policy import DEFAULT_ACTIONS


def test_metadata_only_storage(tmp_path):
    path=tmp_path/'secure.sqlite3';s=Store(path)
    eid=s.event('inspector','redacted',{'email':1},1)
    assert eid
    events=s.events()
    assert len(events)==1 and events[0]['categories']=={'email':1}
    assert b'jane@example.com' not in path.read_bytes()
    assert s.statistics()['redacted']==1
    assert s.purge(0)==1
    assert s.statistics()['total']==0
    s.close()


def test_store_policies(tmp_path):
    s=Store(tmp_path/'audit.db')
    assert s.get_actions()==DEFAULT_ACTIONS
    actions=dict(DEFAULT_ACTIONS);actions['email']='block'
    s.set_actions(actions)
    assert s.get_actions()['email']=='block'
    s.close()
    s=Store(tmp_path/'audit.db')
    assert s.get_actions()['email']=='block'
    s.close()
