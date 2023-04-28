"""
Defines routes to gather data from config/database
"""

# -----IMPORTS-----
from flask import abort, Blueprint, current_app, jsonify, Response
from extensions.encryption import decrypt_api_key
from extensions import ArcPlus
from models import Site, Channel


# create Blueprint object
api = Blueprint('api', __name__)


# ----- BURK API CALL -----
@api.route('/burk/<int:site_id>/')
async def api_call(site_id: int):
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
        # Add values to the channel dict based on information from Burk
        burk_data = get_burk_data(site, meters, statuses)
        return burk_data


# ----- BURK VALUE SORTING -----
def get_burk_data(site, meters, statuses):
    data = []
    channels = site.channels
    for channel in channels:
        if channel.chan_type == 'meter':
            meter_value = get_meter_value(channel, meters)
            channel_data = channel.to_dict()
            channel_data['html_tag'] = f'S{site.id}*C{channel.id}'
            channel_data['value'] = meter_value
            data.append(channel_data)
        elif channel.chan_type == 'status':
            status_values = get_status_value(channel, statuses)
            channel_data = channel.to_dict()
            channel_data['html_tag'] = f'S{site.id}*C{channel.id}'
            channel_data['value'] = status_values
            data.append(channel_data)
    return data


def get_meter_value(channel: Channel, meters: list[dict]):
    """ Using meter values from Burk API call, append value to channel """
    try:
        config = channel.meter_config[0]
        num = config.burk_channel
        meter_value = meters[num - 1]['value']
    except IndexError:
        current_app.logger.info(f'Meter Channel {channel.id} at Site {channel.site_id} Burk Data index error')
        meter_value = None
    return meter_value


def get_status_value(channel: Channel, statuses: list[dict]):
    """ Using status values from Burk API, append value to channel """
    status_values = []
    for i, option in enumerate(channel.status_options):
        try:
            num = option.burk_channel
            if not num:
                status_values.append(None)
                continue
            status_value = statuses[num - 1]['value']
            status_values.append(status_value)
        except IndexError:
            current_app.logger.info(f'Status Channel {channel.id} at Site {channel.site_id} Burk Data index error')
    return status_values


# ----- CHANNEL CONFIGURATION OPTIONS -----
# Anything added to units or colors will be available in config settings
@api.route('/colors')
def get_colors():
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
def get_units():
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


# ----- Pass data from database to Javascript -----
@api.route('/sites')
def all_sites() -> Response:
    """ Called by JS to get list of site names only """
    sites = Site.query.all()
    from models.schemas import SiteSchema
    schema = SiteSchema(many=True)
    site_data = schema.dump(sites)
    return jsonify(site_data)


# TODO: Adjust ma.Schemas to combine channels
@api.route('/<int:site_id>/channel/<int:channel_id>')
def get_channel_data(site_id, channel_id):
    try:
        site = Site.query.get_or_404(site_id)
        channel = Channel.query.get_or_404(channel_id)
    except Exception as e:
        print(e)
        return abort(400, 'Database query failed')
    data = channel.to_dict()
    data['site_name'] = site.site_name
    return data


@api.route('/channel_config/<int:channel_id>')
def get_channel_config(channel_id):
    channel = Channel.query.get_or_404(channel_id)
    config = []
    if channel.chan_type == 'meter':
        for option in channel.meter_config:
            config.append(option.to_dict())
    elif channel.chan_type == 'status':
        for option in channel.status_options:
            config.append(option.to_dict())
    return config


@api.route('/channel/<int:channel_id>/readings')
def get_readings_for_channel(channel_id):
    """ Get list of all reading values for a specific channel id """
    # TODO: Only load a specific amount of reading values
    from models import Reading
    channel = Channel.query.get(channel_id)
    values = [chan_value.to_dict() for chan_value in channel.reading_values]
    for value in values:
        reading = Reading.query.get(value['reading_id'])
        reading_date = reading.timestamp
        value['timestamp'] = reading_date
    return jsonify(values)

# ------------------ DELETE ONCE VERIFIED NOT IN USE --------------------------------
# def get_setup_channels(results):
#     """ Gather the correct setup dependent on site_type"""
#     if results['site_type'] == 'fm':
#         setup_channels = get_fm_setup_channels()
#         if results.get('pilot_id'):
#             setup_channels.append({'html_tag': 'pilot', 'type': 'status', 'title': 'Pilot'})
#     elif results['site_type'] == 'am':
#         setup_channels = get_am_setup_channels()
#     else:
#         raise Exception('Insufficient Data')
#     return setup_channels
#
#
# @api.route('/fm_setup_channels')
# def get_fm_setup_channels():
#     """ Used by JS to determine standard channels for FM site """
#     fm_channels = [
#         {'html_tag': 'oa_tx', 'type': 'status', 'title': 'On Air TX'},
#         {'html_tag': 'ant_fwd', 'type': 'meter', 'title': 'Antenna Forward Power'},
#         {'html_tag': 'ant_ref', 'type': 'meter', 'title': 'Antenna Reflected Power'},
#         {'html_tag': 'temp', 'type': 'meter', 'title': 'Rack Temp'},
#         {'html_tag': 'pa_volts', 'type': 'meter', 'title': 'PA Voltage'},
#         {'html_tag': 'pa_amps', 'type': 'meter', 'title': 'PA Current'},
#     ]
#     return fm_channels
#
#
# @api.route('/am_setup_channels')
# def get_am_setup_channels():
#     """ Used by JS to determine standard channels for AM site """
#     am_channels = [
#         {'html_tag': 'oa_tx', 'type': 'status', 'title': 'On Air TX'},
#         {'html_tag': 'ant_fwd', 'type': 'meter', 'title': 'Antenna Forward Power'},
#         {'html_tag': 'ant_ref', 'type': 'meter', 'title': 'Antenna Reflected Power'},
#         {'html_tag': 'temp', 'type': 'meter', 'title': 'Rack Temp'},
#         {'html_tag': 'common_pt', 'type': 'meter', 'title': 'Common Point'},
#         {'html_tag': 't1_current', 'type': 'meter', 'title': 'Tower 1 Current'},
#         {'html_tag': 't1_phase', 'type': 'meter', 'title': 'Tower 1 Phase'},
#         {'html_tag': 't2_current', 'type': 'meter', 'title': 'Tower 2 Base Current'},
#         {'html_tag': 't3_current', 'type': 'meter', 'title': 'Tower 3 Current'},
#         {'html_tag': 't3_phase', 'type': 'meter', 'title': 'Tower 3 Phase'},
#         {'html_tag': 'pattern', 'type': 'status', 'title': 'Pattern'}
#     ]
#     return am_channels
#
#
# def sort_channel_data(results, setup_channels) -> list[dict]:
#     """
#     Gathers channel data from form submit results
#     Adds sorts data based on dictionary of channels
#     """
#     channels = []
#     for chan in setup_channels:
#         html_tag = chan['html_tag']
#         channel = {
#             'title': results[f'{html_tag}_title'],
#             'id_name': results[f'{html_tag}_id'],
#             'type': results[f'{html_tag}_type']
#         }
#         if chan['type'] == 'meter':
#             meter_config = dict(
#                 units=results[f'{html_tag}_units'],
#                 burk_channel=int(results[f'{html_tag}_num']),
#                 nominal=float(results[f'{html_tag}_nominal']),
#                 upper_limit=float(results[f'{html_tag}_upper']),
#                 upper_color=results.get(f'{html_tag}_upper_color'),
#                 lower_limit=float(results[f'{html_tag}_lower']),
#                 lower_color=results[f'{html_tag}_lower_color'],
#             )
#             channel['meter_config'] = meter_config
#         elif chan['type'] == 'status':
#             options = get_options(html_tag, results)
#             channel['options'] = options
#         channels.append(channel)
#     return channels
#
