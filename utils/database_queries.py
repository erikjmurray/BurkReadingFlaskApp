# ---- BUILT IN IMPORTS -----
from datetime import datetime
from typing import List, Optional, Tuple

# ----- PROJECT IMPORTS -----
from models import Dasdec, EAS, Reading, Site


# ----- SQL Queries -----
def query_readings_by_date(date: datetime) -> List[Reading]:
    """ Queries SQL that match a specific date """
    # if timestamp between 00:00:00:00.. and 23:59:59:99.. return data
    start_datetime = datetime.combine(date, datetime.min.time())
    end_datetime = datetime.combine(date, datetime.max.time())
    readings = Reading.query.filter(Reading.timestamp >= start_datetime, Reading.timestamp <= end_datetime).all()

    return readings


def query_readings_by_date_range(dates: Tuple[datetime, datetime]) -> List[Reading]:
    """ Queries SQL for a range of dates worth of readings """
    readings = Reading.query.filter(Reading.timestamp >= dates[0], Reading.timestamp <= dates[1]).all()
    return readings


def query_eas_tests_by_date_range(dates: Tuple[datetime, datetime], site: Optional[Site] = None) -> List[EAS]:
    """ Queries SQL for EAS Tests transmitted on the site for a specific range of dates
    """
    if site:
        eas_tests = EAS.query.join(EAS.sites).filter(
            Site.id == site.id,
            EAS.started >= dates[0],
            EAS.ended <= dates[1]
        ).order_by(
            EAS.started.asc()
        ).all()
    else:
        eas_tests = EAS.query.filter(EAS.started >= dates[0], EAS.ended <= dates[1]).all()
    return eas_tests


def query_dasdecs_by_id(dasdec_ids: list) -> List[Dasdec]:
    """  """
    dasdecs = []
    for _id in dasdec_ids:
        try:
            dasdec = Dasdec.query.get(_id)
            dasdecs.append(dasdec)
        except:
            continue
    return dasdecs
