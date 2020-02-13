def seconds_to_complete_time(seconds, ms=False):
    """
    Breaks down an amount of time represented in seconds into hours, minutes, seconds and milliseconds (if ms=True). This time is returned as a tuple.

    Returns:
        A tuple of (hours, minutes, seconds, <milliseconds>)
    """

    h = int(seconds / 3600)
    m = int((seconds % 3600) / 60)
    s = seconds % 3600 % 60

    if ms:
        ms = (s - int(s)) * 1000
        s = int(s)

    if ms:
        return (h, m, s, ms)
    else:
        return (h, m, s)
