from sparkprivacy.reports import make_pdf
from sparkprivacy.policy import DEFAULT_ACTIONS


def test_report_is_metadata_only():
    p=make_pdf({'total':1,'blocked':0,'redacted':1,'allowed':0,'observed':0},
               [{'at':'2026-10-25T00:00:00+00:00','channel':'inspector','disposition':'redacted','count':1,'categories':{'email':1}}], DEFAULT_ACTIONS)
    assert p[:4]==b'%PDF' and len(p)>1000
