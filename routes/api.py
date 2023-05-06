"""
Defines routes to gather data from config/database
"""
# ----- 3RD PARTY IMPORTS-----
from flask import abort, Blueprint, current_app, jsonify, Response
# ----- BUILT IN IMPORTS -----
from typing import List
# ----- PROJECT IMPORTS -----
from utils.encryption import decrypt_api_key
from utils import ArcPlus
from models import Site, Channel
from models.schemas import SiteSchema, ChannelSchema, MeterConfigSchema, StatusOptionSchema

# create Blueprint object
api = Blueprint('api', __name__)


# ----- BURK API CALL -----
@api.route('/burk/<int:site_id>/')
async def burk_api_call(site_id: int) -> List[dict]:
    """
    Call API for meter and status data from Burk
    Sort and add data to channels based on extensions setup
    """
    site = Site.query.get_or_404(site_id)
    api_key = decrypt_api_key(site.api_key)

    # Get data from Burk unit
    arcplus = ArcPlus(ip=site.ip_addr, api_key=api_key)
    meters, statuses = await arcplus.get_meters_and_status()

    if not meters and not statuses:
        return abort(400, f'Could not connect to {site.site_name}')
    else:
        burk_data = get_burk_data(site, meters, statuses)
        return burk_data


# ----- BURK VALUE SORTING -----
def get_burk_data(site: Site, meters: list, statuses: list) -> List[dict]:
    data = []
    channel_schema = ChannelSchema(many=True)
    channels = channel_schema.dump(site.channels)
    for channel in channels:
        if channel['chan_type'] == 'meter':
            meter_value = get_meter_value(channel, meters)
            channel['value'] = meter_value
            data.append(channel)
        elif channel['chan_type'] == 'status':
            status_values = get_status_value(channel, statuses)
            channel['value'] = status_values
            data.append(channel)
    return data


def get_meter_value(channel: Channel, meters: List[dict]) -> str:
    """ Using meter values from Burk API call, append value to channel """
    try:
        burk_channel = channel['meter_config'][0]['burk_channel']
        meter_value = meters[burk_channel - 1]['value']
    except IndexError:
        current_app.logger.info(f'Meter Channel {channel.id} at Site {channel.site_id} Burk Data index error')
        meter_value = None
    return meter_value


def get_status_value(channel: Channel, statuses: List[dict]) -> List[str]:
    """ Using status values from Burk API, append value to channel """
    status_values = []
    for i, option in enumerate(channel['status_options']):
        try:
            burk_channel = option['burk_channel']
            if not burk_channel:
                status_values.append(None)
                continue
            status_value = statuses[burk_channel - 1]['value']
            status_values.append(status_value)
        except IndexError:
            current_app.logger.info(f'Status Channel {channel.id} at Site {channel.site_id} Burk Data index error')
    return status_values


# ----- Pass data from database to Javascript -----
@api.route('/sites')
def all_sites() -> Response:
    """ Called by JS to get list of site names only """
    sites = Site.query.all()
    schema = SiteSchema(many=True)
    site_data = schema.dump(sites)
    return jsonify(site_data)


@api.route('/site/<int:site_id>/channels')
def all_site_channels(site_id: int) -> Response:
    """ Called by JS on site refresh failure to connect """
    channels = Channel.query.filter_by(site_id=site_id).all()
    channel_schema = ChannelSchema(many=True)
    channel_data = channel_schema.dump(channels)
    return jsonify(channel_data)


@api.route('/channel/<int:channel_id>')
def get_channel_data(channel_id: int) -> Response:
    channel = Channel.query.get_or_404(channel_id)
    channel_schema = ChannelSchema()
    channel_data = channel_schema.dump(channel)
    return jsonify(channel_data)


@api.route('/channel_config/<int:channel_id>')
def get_channel_config(channel_id: int) -> Response:
    channel = Channel.query.get_or_404(channel_id)
    if channel.chan_type == 'meter':
        config_schema = MeterConfigSchema(many=True)
        config_data = config_schema.dump(channel.meter_config)
        return jsonify(config_data)
    elif channel.chan_type == 'status':
        option_schema = StatusOptionSchema(many=True)
        option_data = option_schema.dump(channel.status_options)
        return jsonify(option_data)
    return jsonify({'error': 'Undefined channel type'})


# ----- CHANNEL CONFIGURATION OPTIONS -----
# Anything added to units or colors will be available in config settings
@api.route('/colors')
def get_colors() -> List[dict]:
    """ Background color options for config """
    colors = [
        {'hex': 'transparent', 'name': 'None'},
        {'hex': "#00ff00", 'name': "Green"},
        {'hex': "#ffff00", 'name': "Yellow"},
        {'hex': "#ff1717", 'name': "Red"},
        {'hex': "#00ffff", 'name': 'Blue'},
        {'hex': "#ff8c00", 'name': 'Orange'}
    ]
    return colors


@api.route('/units')
def get_units() -> list:
    """ Options for units in channel config """
    units = [
        'kW',
        'Watts',
        'Deg',
        'mA',
        'Amps',
        'Volts',
    ]
    return units


# ----- THIS WAS A TEST ROUTE TO GET VALUES FOR SPECIFIC CHANNEL
# @api.route('/channel/<int:channel_id>/readings')
# def get_readings_for_channel(channel_id):
#     """ Get list of all reading values for a specific channel id """
#     # TODO: Only load a specific amount of reading values
#     from models import Reading
#     channel = Channel.query.get(channel_id)
#     values = [chan_value.to_dict() for chan_value in channel.reading_values]
#     for value in values:
#         reading = Reading.query.get(value['reading_id'])
#         reading_date = reading.timestamp
#         value['timestamp'] = reading_date
#     return jsonify(values)
