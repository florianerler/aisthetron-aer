from time import time

EPOCH_OFFSET = 946684800 #offset between micropython and python unixtime

SYNC_THRESHOLD = 1704063600 #unix date 01.01.2024 MEZ threshold

def get_timestamp():
    """
    Return the current unix time and the sync status of the clock.

    The status is "sync" if the time is at or after SYNC_THRESHOLD,
    otherwise "async" (clock not yet set after boot).

    Returns:
        tuple: (unix_time, status) with status "sync" or "async"
    """
    unix_time = time() + EPOCH_OFFSET
    if unix_time >= SYNC_THRESHOLD:
        return (unix_time, "sync")
    else:
        return (unix_time, "async")
