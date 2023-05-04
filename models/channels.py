"""
SQL Table definitions for configuration.
"""
from extensions import db, ma
from models.readings import ReadingValue


class Channel(db.Model):
    """
    Channel definitions
    Can be either meter or status definition
    Reference meter config or status options table for details
    """
    __tablename__ = 'channels'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    chan_type = db.Column(db.String(8), nullable=False)  # 'meter' or 'status'
    channel_order = db.Column(db.Integer, nullable=False)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)

    meter_config = db.relationship('MeterConfig', backref='channel', lazy=True)
    status_options = db.relationship('StatusOption', backref='channel', lazy=True)
    reading_values = db.relationship('ReadingValue', backref='channel', lazy=True)


    def __init__(self, chan_type, title, site_id):
        self.title = title
        self.chan_type = chan_type
        self.site_id = site_id
        self.channel_order = self.get_next_channel_order(site_id)


    def get_next_channel_order(self, site_id):
        max_channel_order = Channel.query.filter_by(site_id=site_id).with_entities(db.func.max(Channel.channel_order)).scalar()
        if max_channel_order is None:
            return 0
        else:
            return max_channel_order + 1


class MeterConfig(db.Model):
    """
    Define config for meter channel
    """
    __tablename__ = 'meter_config'
    id = db.Column(db.Integer, primary_key=True)
    burk_channel = db.Column(db.Integer, nullable=False)
    units = db.Column(db.String(10), nullable=False)
    nominal_output = db.Column(db.Float, nullable=False)
    upper_limit = db.Column(db.Float, nullable=False)
    upper_lim_color = db.Column(db.String(15), nullable=False)
    lower_limit = db.Column(db.Float, nullable=False)
    lower_lim_color = db.Column(db.String(15), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=False)


class StatusOption(db.Model):
    """
    Define config for option selection for status channel
    Note: Status channel can have multiple options
    """
    __tablename__ = 'status_options'
    id = db.Column(db.Integer, primary_key=True)
    burk_channel = db.Column(db.Integer, nullable=False)
    selected_value = db.Column(db.String(50), nullable=False)
    selected_state = db.Column(db.Boolean, nullable=False)
    selected_color = db.Column(db.String(15), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=False)


