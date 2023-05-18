
# ----- BUILT IN IMPORTS -----
from datetime import datetime


def input_dates_to_datetime(date_string: str) -> datetime:
    """ Converts string date input to datetime object """
    date_format = '%Y-%m-%d %H:%M:%S'
    date_as_datetime_obj = datetime.strptime(date_string, date_format)
    return date_as_datetime_obj


def iso_input_to_datetime(timestamp: str) -> datetime:
    """ Converts HTML Input to Python datetime object """
    return datetime.fromisoformat(timestamp.replace('T', ' '))
