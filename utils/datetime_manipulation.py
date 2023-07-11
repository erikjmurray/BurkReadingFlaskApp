# ----- BUILT IN IMPORTS -----
from datetime import datetime, timedelta
from typing import List


def input_dates_to_datetime(date_string: str) -> datetime:
    """ Converts string date input to datetime object """
    date_format = '%Y-%m-%d %H:%M:%S'
    date_as_datetime_obj = datetime.strptime(date_string, date_format)
    return date_as_datetime_obj


def iso_input_to_datetime(timestamp: str) -> datetime:
    """ Converts HTML Input to Python datetime object """
    return datetime.fromisoformat(timestamp.replace('T', ' '))


def create_list_of_individual_dates(start_date: datetime,
                                    end_date: datetime) -> List[datetime]:
    """ Get a list of datetime objects in a given range """
    dates = []
    while start_date <= end_date:
        dates.append(start_date)
        start_date += timedelta(days=1)
    return dates

# TODO: Verify function with real data
def dasdec_input_to_datetime(timestamp: str) -> datetime:
    """ Converts string input from DASDEC timestamp to Datetime object """
    format_string = "%a %b %d %H:%M:%S %Y %Z"
    datetime_obj = datetime.strptime(timestamp, format_string)
    return datetime_obj

