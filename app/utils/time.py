"""
This module contains the current time variables.
"""

from datetime import datetime
from time import tzname


def current_time_zone():
    """
    Returns the current system time zone as a string.
    """
    return tzname[0]


def current_date():
    """
    Returns the current date as a string in the format "dd.mm.yy".
    """
    return datetime.now().strftime("%d.%m.%y")


def current_time(seconds=False, micro_seconds=False):
    """
    Returns the current time as a string in the format "HH:MM" or "HH:MM:SS" depending on the value of the seconds parameter. If the micro_seconds parameter is set to True, the time will include microseconds as well.
    """
    if not seconds:
        return datetime.now().strftime("%H:%M")
    else:
        if micro_seconds:
            return datetime.now().strftime("%H:%M:%S.%f")
        else:
            return datetime.now().strftime("%H:%M:%S")


def current_time_stamp():
    """
    Returns the current time stamp as an integer.
    """
    time_stamp = datetime.now().timestamp()
    time_stamp = int(time_stamp)
    return time_stamp
