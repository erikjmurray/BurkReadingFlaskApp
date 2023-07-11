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

    def __repr__(self):
        return f"Reading: {self.reading_id}, CH{self.channel_id} | Value: {self.reading_value}"
