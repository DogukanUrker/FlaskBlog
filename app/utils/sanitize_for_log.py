"""
This module contains the function to sanitize untrusted values before they are
written to log output.
"""


def sanitize_for_log(value):
    """Strip CR/LF characters from a value before it is interpolated into a log message.

    Request-derived values (client IPs, URL segments, etc.) are attacker
    controlled. Logging them unsanitized lets an attacker inject carriage
    return / line feed characters and forge fake log lines (CWE-117).
    """

    return str(value).replace("\r", "").replace("\n", "")
