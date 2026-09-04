"""Live-tab rate limits. Session cap via st.session_state; daily cap via a
process-global counter (resets on app reboot - documented; the hard backstop is
the Console spend alert + kill switch)."""
SESSION_CAP = 5
DAILY_CAP = 40


def check(session_count: int, today_count: int) -> tuple[bool, str]:
    if today_count >= DAILY_CAP:
        return False, ("The live demo hit its daily budget cap - try the Showcase tab, "
                       "or come back tomorrow. (The daily cap keeps this demo free to run.)")
    if session_count >= SESSION_CAP:
        return False, ("You've used this session's 5 live questions - the Showcase tab "
                       "has 12 more answers, or refresh later.")
    return True, ""
