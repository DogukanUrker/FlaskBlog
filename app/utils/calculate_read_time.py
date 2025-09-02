"""
This module contains the function to calculate the estimated reading time in minutes for a given post content.
"""

from re import sub


def calculate_read_time(content):
    """Calculate the estimated reading time in minutes for a given post content."""

    clean_text = sub(r"<[^>]+>", "", content)

    word_count = len(clean_text.split())
    reading_time = max(1, round(word_count / 200))

    return reading_time
