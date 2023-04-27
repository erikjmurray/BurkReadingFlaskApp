""" Returns reading data if there was value data for the site on the queried date """
# ----- IMPORTS -----
from models import Message, ReadingValue, User


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

    # returns empty list if no value in the ReadingValue for the reading
    reading_values = []
    for value in values:
        reading_value = value.reading_value if value else None
        reading_values.append(reading_value)

    reading_data['reading_values'] = check_list(reading_values)

    # Add name of User to reading_data
    user = User.query.get(reading.user_id)
    reading_data['user'] = user.name.replace('*', ' ')

    # Add any messsages associated to site from current reading
    messages = Message.query.filter_by(site_id=site.id, reading_id=reading.id).all()
    reading_data['messages'] = list([message.message for message in messages])

    return reading_data


def check_list(input_list):
    """ If all entries empty return, else return None in list as N/A string """
    if all(elem is None for elem in input_list):
        return None
    else:
        return ['N/A' if elem is None else elem for elem in input_list]
