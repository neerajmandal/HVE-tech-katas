def pytest_sessionfinish(session, exitstatus):
    """
    Suppress exit code 5 (no tests collected).
    """
    if exitstatus == 5:
        session.exitstatus = 0
