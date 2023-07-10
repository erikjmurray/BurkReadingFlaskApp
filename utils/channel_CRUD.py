""" Used to create new channels in database from results """
import re
from typing import List, Dict

from models import Channel, MeterConfig, ReadingValue, StatusOption
from extensions import db


def handle_channel_update(results: dict, site_id: int) -> None:
    """
    Given form data and a target site
    Create or update channels associated with site
    """
    channel_data = sort_results_channel_data(results)

    # for channel_id in channel_data['channels_to_delete']:
    #     delete_channel(channel_id)
    for option_id in channel_data['options_to_delete']:
        delete_option(option_id)
    # for channel_id in channel_data['existing_channels']:
    #     channel_data = channel_data['existing_channels'][channel_id]
    #     update_existing_channel(channel_data, channel_id)
    # create_new_channels(channel_data['new_channels'], site_id)
    return


def sort_results_channel_data(results: dict) -> Dict:
    """ Given channel data, sort new and existing channels into associated dictionaries """
    existing_channels = {}
    new_channels = {}
    channels_to_delete = []
    options_to_delete = []

    for key, value in results.items():
        # use regex to match entry in results to existing/new channel tag
        match = re.match(r"(existing|new|delete)_?(option|channel)?_(\d{1,3})_(.*)", key)
        if not match:
            continue
        dict_tag = match.group(1)
        id_tag = int(match.group(3))
        data_tag = match.group(4)
        if dict_tag == 'existing':
            if id_tag not in existing_channels:
                existing_channels[id_tag] = {}
            existing_channels[id_tag][data_tag] = value
        elif dict_tag == 'new':
            if id_tag not in new_channels:
                new_channels[id_tag] = {}
            new_channels[id_tag][data_tag] = value
        elif dict_tag == 'delete':
            if match.group(2) == 'channel':
                channels_to_delete.append(id_tag)
            elif match.group(2) == 'option':
                options_to_delete.append(id_tag)


    channel_data = dict(
        existing_channels=existing_channels,
        new_channels=new_channels,
        channels_to_delete=channels_to_delete,
        options_to_delete=options_to_delete
    )
    return channel_data


def delete_channel(channel_id: int) -> None:
    """ Given a channel id, remove channel and associated config from database """
    channel_to_delete = Channel.query.get(int(channel_id))

    # delete meter configs associated with channel
    meter_config_to_del = MeterConfig.query.filter_by(channel_id=channel_to_delete.id).all()
    for config in meter_config_to_del:
        db.session.delete(config)

    # delete status options associated with channel
    status_opt_to_del = StatusOption.query.filter_by(channel_id=channel_to_delete.id).all()
    for option in status_opt_to_del:
        db.session.delete(option)

    reading_vals_to_del = ReadingValue.query.filter_by(channel_id=channel_to_delete.id).all()
    for reading in reading_vals_to_del:
        db.session.delete(reading)

    # delete channel
    db.session.delete(channel_to_delete)
    db.session.commit()
    return


def delete_option(option_id: int) -> None:
    """ Given an option ID, remove that particular option from the database """
    option_to_delete = StatusOption.query.get(int(option_id))

    # Remove option reference from channel
    associated_channel = Channel.query.get(option_to_delete.channel_id)
    associated_channel.status_options.remove(option_to_delete)

    # commit changes
    db.session.delete(option_to_delete)
    db.session.commit()
    return


def update_existing_channel(channel_data: dict, channel_id: int) -> None:
    channel_to_update = Channel.query.get(channel_id)

    channel_to_update.title = channel_data['title']
    db.session.commit()

    if channel_to_update.chan_type == 'meter':
        meter_configs = MeterConfig.query.filter_by(channel_id=channel_id).all()
        for config in meter_configs:
            update_meter_config(config, channel_data)
    elif channel_to_update.chan_type == 'status':
        status_options = StatusOption.query.filter_by(channel_id=channel_id).all()
        option_data = sort_status_options(channel_data)
        for i, option in enumerate(status_options):
            update_status_option(option, option_data[i])

        if len(option_data) > len(status_options):
            new_option_data = option_data[len(status_options):]
            new_options = []
            for option_data in new_option_data:
                new_option = create_new_status_option(option_data, channel_to_update.id)
                new_options.append(new_option)
            db.session.add_all(new_options)
            db.session.commit()
    return


def update_meter_config(config: MeterConfig, channel_data: dict) -> None:
    """ Given meter config object, adjust values based on form data """
    config.burk_channel = channel_data['burk_channel']
    config.units = channel_data['units']
    config.nominal_output = channel_data['nominal_output']
    config.upper_limit = channel_data['upper_limit']
    config.upper_lim_color = channel_data['upper_lim_color']
    config.lower_limit = channel_data['lower_limit']
    config.lower_lim_color = channel_data['lower_lim_color']

    db.session.commit()  # commit changes to database
    return


def update_status_option(option: StatusOption, option_data: dict) -> None:
    """ Given status option data, adjust values based on form data """
    option.burk_channel = option_data['burk_channel']
    option.selected_value = option_data['selected_value']
    option.selected_state = option_data['selected_state']
    option.selected_color = option_data['selected_color']

    db.session.commit()  # commit changes to database
    return


def create_new_channels(new_channels, site_id: int):
    """ Create new channels from new channel data """
    meter_configs = []
    status_options = []

    for new_channel in new_channels:
        # create new channel object
        channel_data = new_channels[new_channel]
        channel = create_channel(channel_data, site_id)

        # add to channel object to database
        db.session.add(channel)
        db.session.commit()

        # query for new channel in db
        # TODO: Make title unique to site
        target_channel = Channel.query.filter_by(title=channel.title, site_id=site_id).first()

        # associate config/option data to channel
        if channel.chan_type == 'meter':
            meter_config = create_new_meter_config(channel_data, target_channel.id)
            meter_configs.append(meter_config)
        elif channel.chan_type == 'status':
            options = sort_status_options(channel_data)
            for option_data in options:
                status_option = create_new_status_option(option_data, target_channel.id)
                status_options.append(status_option)

        # commit configurations to database
        db.session.add_all(meter_configs)
        db.session.add_all(status_options)
        db.session.commit()
    return


def create_channel(channel_data: dict, site_id: int) -> Channel:
    """ Create new channel given channel data """
    return Channel(
        chan_type=channel_data['chan_type'],
        title=channel_data['title'],
        site_id=site_id
    )


def create_new_meter_config(channel_data: dict, channel_id: int) -> MeterConfig:
    return MeterConfig(
        units=channel_data['units'],
        burk_channel=int(channel_data['burk_channel']),
        nominal_output=float(channel_data['nominal_output']),
        upper_limit=float(channel_data['upper_limit']),
        upper_lim_color=channel_data['upper_lim_color'],
        lower_limit=float(channel_data['lower_limit']),
        lower_lim_color=channel_data['lower_lim_color'],
        channel_id=channel_id,
    )


def create_new_status_option(option_data: dict, channel_id: int) -> StatusOption:
    return StatusOption(
        burk_channel=option_data['burk_channel'],
        selected_value=option_data['selected_value'],
        selected_state=option_data['selected_state'],
        selected_color=option_data['selected_color'],
        channel_id=channel_id,
    )


def sort_status_options(channel_data: dict) -> List[dict]:
    option_counter = int(channel_data['opt_count'])
    options = []
    for count in range(1, option_counter + 1):
        option_data = {
            'burk_channel': int(channel_data[f"burk_channel_{count}"]),
            'selected_value': channel_data[f"selected_value_{count}"],
            'selected_state': True if channel_data[f"selected_state_{count}"] == 'true' else False,
            'selected_color': channel_data[f"selected_color_{count}"],
        }
        options.append(option_data)
    return options
