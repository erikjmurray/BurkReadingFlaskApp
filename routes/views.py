"""
Defines routes to user accessible pages on site
"""
import datetime
import re

# -----IMPORTS-----
from flask import Blueprint, current_app, flash, redirect, render_template, request, jsonify  # abort, session, url_for
from extensions import db
from models import Site, User, Channel, Reading, ReadingValue, Message, EAS
from models.schemas import SiteSchema, UserSchema

# create Blueprint object
views = Blueprint('views', __name__)


# -----ROUTES-----
@views.route('/')
@views.route('/home')
def index():
    return render_template('main/index.html')


@views.route('/readings')
async def readings():
    """Homepage with links to sites from extensions"""
    site_schema = SiteSchema(many=True)
    sites = Site.query.order_by(Site.site_order.asc()).all()
    site_data = site_schema.dump(sites)

    user_schema = UserSchema(many=True)
    operators = User.query.all()
    operator_data = user_schema.dump(operators)
    return render_template('main/readings.html', sites=site_data, operators=operator_data)


@views.route('/readings', methods=['POST'])
def readings_post():
    """ Details posting data from homepage form """
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
    return redirect('/readings')


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
            reading_value=value,
            channel_id=channel_id,
            reading_id=reading.id
        ))
    for value in channel_values:
        try:
            db.session.add(value)
            db.session.commit()
        except Exception as e:
            # if failure rollback commit and flash error message
            db.session.rollback()
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
            db.session.rollback()
            message = f"Automated messages for {site.site_name} failed to post"
            error_messages.append(message)
    return error_messages


@views.route('/site/<int:site_id>/readings')
async def site(site_id):
    site = Site.query.get_or_404(site_id)
    site_schema = SiteSchema()
    site_data = site_schema.dump(site)

    # get the 12 most recent readings from the database
    readings = Reading.query.order_by(Reading.timestamp.desc()).limit(12).all()

    from extensions import get_valid_readings
    reading_data = get_valid_readings(readings, site)

    return render_template('main/site.html', site=site_data, channels=site_data['channels'], readings=reading_data)


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








