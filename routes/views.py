"""
Defines routes to user accessible pages on site
"""
import datetime
import re

# -----IMPORTS-----
from flask import Blueprint, current_app, flash, redirect, render_template, request, jsonify      # abort, session, url_for
from extensions import db
from models import Site, User, Channel, Reading, ReadingValue, Message, EAS

# create Blueprint object
views = Blueprint('views', __name__)

# -----ROUTES-----
@views.route('/')
@views.route('/home')
async def home():
    """Homepage with links to sites from extensions"""
    sites = Site.query.order_by(Site.site_order.asc()).all()
    # TODO: Filter off Users by privilege i.e. Admins do not show up in drop down.
    operators = User.query.all()
    return render_template('main/home.html', sites=sites, operators=operators)


@views.route('/', methods=['POST'])
@views.route('/home', methods=['POST'])
def home_post():
    """ Details posting data from homepage form """
    # TODO: Implement Flask WTF for form validation
    # get input data from form
    form_data = request.form
    timestamp = datetime.datetime.now()

    # Attempt to post data to database, return any error to flash to User
    reading_errors = post_reading(form_data, timestamp)
    reading = Reading.query.filter_by(timestamp=timestamp).first()

    value_errors = post_channel_values(form_data, reading)
    message_errors = post_messages(form_data, reading)

    error_messages = reading_errors + value_errors + message_errors
    # Displays error message if any, else database post successful
    if error_messages:
        for error in error_messages:
            flash(error)
    else:
        flash('Post to database successful!')
    return redirect('/')


def post_reading(form_data, timestamp):
    """ Create reading object and post the database """
    error_messages = []
    reading = Reading(
        timestamp=timestamp,
        notes=form_data['notes'],
        user_id=int(form_data['mceod'])
    )
    try:
        db.session.add(reading)
        db.session.commit()
    except Exception as e:
        # if failure rollback commit and flash error message
        current_app.logger.error(e)
        db.session.rollback()
        message = f"Reading post failed"
        error_messages.append(message)
    return error_messages


def post_channel_values(form_data, reading):
    """ Post readings values for channels """
    channel_values = []
    error_messages = []
    regex_pattern = r'S(\d+)\*C(\d+)'

    for key, value in form_data.items():
        # ignore any input that is not a channel input
        match = re.match(regex_pattern, key)
        if not match:
            continue
        # gets channel id from input html tag
        channel_id = int(match.group(2))
        channel_values.append(ReadingValue(
            value=value,
            channel_id=channel_id,
            reading_id=reading.id
        ))
    for value in channel_values:
        try:
            db.session.add(value)
            db.session.commit()
        except Exception as e:
            # if failure rollback commit and flash error message
            current_app.logger.error(e)
            db.session.rollback()
            # TODO: More descriptive error message
            message = f"Channel {value.channel_id} post failed"
            error_messages.append(message)
    return error_messages


def post_messages(results, reading):
    """ Sort auto-generate messages by site and post to DB"""
    messages = results.get('messages').splitlines()
    sites = Site.query.all()
    error_messages = []
    for site in sites:
        site_name = site.site_name.replace('_', ' ')
        site_messages = []
        for message in messages:
            if site_name in message:
                print(message)
                site_messages.append(Message(
                    message=message,
                    site_id=site.id,
                    reading_id=reading.id
                ))
        try:
            db.session.add_all(site_messages)
            db.session.commit()
        except Exception as e:
            # if failure rollback commit and flash error message
            current_app.logger.error(e)
            db.session.rollback()
            message = f"Automated messages for {site.site_name} failed to post"
            error_messages.append(message)
    return error_messages


@views.route('/site/<int:site_id>/readings')
async def site(site_id):
    site = Site.query.get_or_404(site_id)
    # get the 12 most recent readings from the database
    readings = Reading.query.order_by(Reading.timestamp.desc()).limit(12).all()

    reading_data = get_valid_readings(readings, site)

    return render_template('main/site.html', site=site, channels=site.channels, readings=reading_data)


def get_valid_readings(readings, site):
    """ Returns non-null readings data from gather_reading_data """
    output_data = []
    for reading in readings:
        reading_data = gather_reading_data(reading, site)
        # only return output if there is valid data in the channel_values list
        if reading_data['reading_values']:
            output_data.append(reading_data)
    return output_data


def gather_reading_data(reading, site):
    """ Gather readings data associated to specific site """
    # Create dict
    reading_data = reading.to_dict()

    # Add the values for each channel to the reading_data
    values = []
    for channel in site.channels:
        values.append(ReadingValue.query.filter_by(channel_id=channel.id, reading_id=reading.id).first())

    # returns empty list if no value in the ChannelValue for the reading
    reading_data['reading_values'] = list([value.reading_value for value in values if value])

    # Add name of User to reading_data
    user = User.query.get(reading.user_id)
    reading_data['user'] = user.name.replace('*', ' ')

    # Add any messsages associated to site from current reading
    messages = Message.query.filter_by(site_id=site.id, reading_id=reading.id).all()
    reading_data['messages'] = list([message.message for message in messages])

    return reading_data


@views.route('/site/<int:site_id>/eas_tests/')
def site_eas_tests(site_id):
    """ Displays the twelve most recent EAS tests"""
    site = Site.query.get(site_id)

    eas_tests = EAS.query.join(EAS.sites).filter(
        Site.id == site_id
    ).order_by(
        EAS.tx_timestamp.desc()
    ).limit(12).all()

    return render_template('main/eas_by_site.html', site=site, eas_tests=eas_tests)


@views.route('/eas')
def eas_render():
    sites = Site.query.order_by(Site.site_order.asc()).all()
    current_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M')
    return render_template('main/eas.html', sites=sites, current_time=current_time)


@views.route('/eas', methods=['POST'])
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
        current_app.logger.warn(e)
        error_message = 'Something went wrong adding the test to the database. Contact local admin'
        error_messages.append(error_message)

    if error_messages:
        for message in error_messages:
            flash(message)
    else:
        flash('Success!')

    return redirect('/eas')


def input_to_datetime(timestamp):
    """ Converts HTML Input to Python datetime object """
    return datetime.datetime.fromisoformat(timestamp.replace('T', ' '))


@views.route('/eas/log/<start_date>/<end_date>')
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





