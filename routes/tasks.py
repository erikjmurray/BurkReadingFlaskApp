"""
Executes tasks such as PDF generation and EAS Log Parsing
"""
# ----- 3RD PARTY IMPORTS -----
from flask import Blueprint, make_response, render_template, Response

# ----- PROJECT IMPORTS -----
from models import Site
from utils.datetime_manipulation import input_dates_to_datetime
from utils.tasks import create_pdf


# create Blueprint object
tasks = Blueprint('tasks', __name__)


@tasks.route('generate_pdf/<int:site_id>/<start_date>/<end_date>')
def generate_pdf(site_id: int,
                 start_date: str,
                 end_date: str) -> Response:
    """ Route to initiate PDF report of site readings for a date range """
    site = Site.query.get(site_id)

    # convert from string format to datetime format
    date_range = (input_dates_to_datetime(start_date), input_dates_to_datetime(end_date))

    pdf_data = create_pdf(site, date_range)

    # Create response object
    response = make_response(pdf_data)
    response.headers.set('Content-Type', 'application/pdf')
    filename = f"{start_date[:-9]}_to_{end_date[:-9]}_{site.site_name}_report.pdf"          # indexing removes hh:mm:ss
    response.headers.set('Content-Disposition', 'attachment', filename=filename)

    return response

