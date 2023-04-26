"""
Create SQL table for readings of both the meter type and status type
"""
from extensions import db


# ----- READINGS -----
class Reading(db.Model):
    """
    Given a site with channel config
    Gather the global information and readings values
    Create database entry referencing readings.
    """
    __tablename__ = 'readings'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # MCEOD
    messages = db.relationship('Message', backref='reading', lazy=True)
    reading_values = db.relationship('ReadingValue', backref='reading', lazy=True)

    def to_dict(self):
        return dict(
            id=self.id,
            timestamp=self.timestamp,
            notes=self.notes,
            user_id=self.user_id
        )

    def __repr__(self):
        return f"Reading {self.id} submitted {self.timestamp.strftime('%m-%d-%Y %H:%M')} by user {self.user_id}"


class Message(db.Model):
    """
    Record of any auto-generated messages for a site during a reading
    """
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)
    reading_id = db.Column(db.Integer, db.ForeignKey('readings.id'), nullable=False)

    def to_dict(self):
        return dict(
            id=self.id,
            message=self.message,
            site_id=self.site_id,
            reading_id=self.reading_id
        )

    def __repr__(self):
        return f"Reading: {self.reading_id} | Message: {self.message}"


class ReadingValue(db.Model):
    """
    For any given channel, store submitted data as a string referencing reading and channel ids
    """
    __tablename__ = 'reading_values'
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), primary_key=True)
    reading_id = db.Column(db.Integer, db.ForeignKey('readings.id'), primary_key=True)
    reading_value = db.Column(db.String(250), nullable=False)

    def to_dict(self):
        return dict(
            reading_value=self.reading_value,
            channel_id=self.channel_id,
            reading_id=self.reading_id
        )

    def __repr__(self):
        return f"Reading: {self.reading_id}, CH{self.channel_id} | Value: {self.reading_value}"


# Association table creating a many-to-many relationship between EAS and Site
eas_site_association = db.Table('eas_site_association',
    db.Column('eas_id', db.Integer, db.ForeignKey('eas_tests.id')),
    db.Column('site_id', db.Integer, db.ForeignKey('sites.id'))
)


class EAS(db.Model):
    """ Model for submitted EAS tests """
    __tablename__ = 'eas_tests'
    id = db.Column(db.Integer, primary_key=True)
    originating = db.Column(db.Boolean, nullable=False)
    test_type = db.Column(db.String(10), nullable=False)    # Consider what test types there are
    rx_from = db.Column(db.String(50), nullable=True)       # make nullable only if originating = False
    rx_timestamp = db.Column(db.DateTime, nullable=True)    # make nullable only if originating = False
    tx_timestamp = db.Column(db.DateTime, nullable=False)
    sites = db.relationship('Site', secondary=eas_site_association, backref='eas_tests', lazy=True)

    def to_dict(self):
        return dict(
            id=self.id,
            originating=True if self.originating else False,
            test_type=self.test_type,
            rx_from=self.rx_from,
            rx_timestamp=self.rx_timestamp,
            tx_timestamp=self.tx_timestamp,
            sites=[site.site_name for site in self.sites]
        )





