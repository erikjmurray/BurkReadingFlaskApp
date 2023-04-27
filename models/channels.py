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
    chan_type = db.Column(db.String(8), nullable=False)  # 'meter' or 'status'
    title = db.Column(db.String(50), nullable=False)
    meter_config = db.relationship('MeterConfig', backref='channel', lazy=True)
    status_options = db.relationship('StatusOption', backref='channel', lazy=True)
    reading_values = db.relationship('ReadingValue', backref='channel', lazy=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)

    def to_dict(self):
        return dict(
            id=self.id,
            chan_type=self.chan_type,
            title=self.title,
            meter_config=[config.id for config in self.meter_config],
            status_options=[opt.id for opt in self.status_options],
            site_id=self.site_id,
        )


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

    def to_dict(self):
        return {
            'id': self.id,
            'burk_channel': self.burk_channel,
            'units': self.units,
            'nominal_output': self.nominal_output,
            'upper_limit': self.upper_limit,
            'upper_lim_color': self.upper_lim_color,
            'lower_limit': self.lower_limit,
            'lower_lim_color': self.lower_lim_color,
        }


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

    def to_dict(self):
        return {
            'id': self.id,
            'burk_channel': self.burk_channel,
            'selected_value': self.selected_value,
            'selected_state': self.selected_state,
            'selected_color': self.selected_color,
        }

