from time import time

EPOCH_OFFSET = 946684800 #offset between micropython and python unixtime

SYNC_THRESHOLD = 1704063600 #unix date 01.01.2024 MEZ threshold

def get_timestamp():
    unix_time = time() + EPOCH_OFFSET
    if unix_time >= SYNC_THRESHOLD:
        return (unix_time, "sync")
    else:
        return (unix_time, "async")
