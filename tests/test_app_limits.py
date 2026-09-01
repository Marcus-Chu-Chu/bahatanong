from app.limits import DAILY_CAP, SESSION_CAP, check


def test_under_caps_allowed():
    ok, msg = check(session_count=0, today_count=0)
    assert ok


def test_session_cap_blocks():
    ok, msg = check(session_count=SESSION_CAP, today_count=1)
    assert not ok and "session" in msg.lower()


def test_daily_cap_blocks():
    ok, msg = check(session_count=0, today_count=DAILY_CAP)
    assert not ok and "today" in msg.lower()
