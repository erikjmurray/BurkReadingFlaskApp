""" Details routes regarding EAS pages """
# ----- 3RD PARTY IMPORTS -----
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required

# ----- BUILT IN IMPORTS -----
from datetime import datetime

# ----- PROJECT IMPORTS -----
from extensions import db
from models import Dasdec, EAS, Site, User
from models.schemas import SiteSchema, UserSchema
from utils.tasks import parse_eas_data, run_async_scraper
from utils.database_queries import query_eas_tests_by_date_range, query_dasdecs_by_id
from utils.datetime_manipulation import input_dates_to_datetime, iso_input_to_datetime

# Initialize Blueprint
eas = Blueprint('eas', __name__)


@eas.route('/eas')
@login_required
def eas_form():
    site_schema = SiteSchema(many=True)
    sites = Site.query.order_by(Site.site_order.asc()).all()
    site_data = site_schema.dump(sites)

    user_schema = UserSchema(many=True)
    operators = User.query.filter_by(is_operator=True).order_by(User.last_name).all()
    operator_data = user_schema.dump(operators)

    # TODO: Create dasdec schema
    # dasdec_schema = DasdecSchema(many=True)
    dasdecs = Dasdec.query.all()
    # dasdec_data = dasdec_schema.dump(dasdecs)

    # Current time used as a default value for receive or transmitted.
    current_time = datetime.now().strftime('%Y-%m-%dT%H:%M')
    return render_template('main/eas_form.html',
                           sites=site_data,
                           current_time=current_time,
                           operators=operator_data,
                           dasdecs=dasdecs)


@eas.route('/eas', methods=['POST'])
def eas_post():
    form_data = request.form
    error_messages = []

    try:
        originating = True if form_data.get('originating') else False

        eas_test = EAS(
            originating=originating,
            test_type=form_data.get('test_type'),
            rx_from=form_data.get('eas_from') if not originating else None,
            rx_timestamp=iso_input_to_datetime(form_data.get('eas_time_rx')) if not originating else None,
            tx_timestamp=iso_input_to_datetime(form_data.get('eas_time_tx'))
        )

        sites = Site.query.all()
        for site in sites:
            if site.site_name in form_data:
                eas_test.sites.append(site)

        db.session.add(eas_test)
        db.session.commit()
    except Exception as e:
        current_app.logger.warning(e)
        error_message = 'Something went wrong adding the test to the database. Contact local admin'
        error_messages.append(error_message)

    if error_messages:
        for message in error_messages:
            flash(message)
    else:
        flash('Success!')

    return redirect(url_for('eas.eas_form'))


@eas.route('/eas/log/<start_date>/<end_date>')
def eas_log(start_date: str, end_date: str):
    """ Gets log of EAS tests for Date Range """
    date_range = (input_dates_to_datetime(start_date), input_dates_to_datetime(end_date))
    tests_for_dates = query_eas_tests_by_date_range(date_range)

    return render_template('main/eas_log.html', eas_tests=tests_for_dates)


@eas.route('/eas/parse/', methods=['POST'])
def display_parsed_dasdec_data() -> str:
    """ Route to initiate PDF report of site readings for a date range """
    dasdec_ids = request.form.getlist('dasdec_ids')   # TODO: Create form for DASDEC selection

    # query dasdecs for new tests
    dasdecs = query_dasdecs_by_id(dasdec_ids)
    results = run_async_scraper(dasdecs)

    eas_data = parse_eas_data(results)

    return render_template('main/eas_dump.html', eas_data=eas_data)


