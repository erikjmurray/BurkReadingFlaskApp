""" Details routes regarding EAS pages """

from datetime import datetime
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required

from extensions import db
from models import Site, EAS


eas = Blueprint('eas', __name__)


@eas.route('/eas')
@login_required
def eas_render():
    sites = Site.query.order_by(Site.site_order.asc()).all()
    current_time = datetime.now().strftime('%Y-%m-%dT%H:%M')
    return render_template('main/eas.html', sites=sites, current_time=current_time)


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
            rx_timestamp=input_to_datetime(form_data.get('eas_time_rx')) if not originating else None,
            tx_timestamp=input_to_datetime(form_data.get('eas_time_tx'))
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

    return redirect(url_for('eas.eas_render'))


def input_to_datetime(timestamp):
    """ Converts HTML Input to Python datetime object """
    return datetime.fromisoformat(timestamp.replace('T', ' '))


@eas.route('/eas/log/<start_date>/<end_date>')
def eas_log(start_date, end_date):
    """ Gets log of EAS tests for Date Range """
    from routes.tasks import input_dates_to_datetime
    date_range = (input_dates_to_datetime(start_date), input_dates_to_datetime(end_date))
    tests_for_dates = query_eas_by_date_range(date_range)

    return render_template('main/all_eas_tests.html', eas_tests=tests_for_dates)


def query_eas_by_date_range(dates):
    """ Gets EAS entries that correspond with specific date range """
    eas_tests = EAS.query.filter(EAS.tx_timestamp >= dates[0], EAS.tx_timestamp <= dates[1]).all()
    return eas_tests
