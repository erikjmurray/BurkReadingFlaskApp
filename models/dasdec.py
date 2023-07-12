""" Details DASDEC model """
# ----- 3RD PARTY IMPORTS -----
from sqlalchemy import BLOB

# ----- PROJECT IMPORTS -----
from extensions import db


class Dasdec(db.Model):
    """ Model for DASDEC data """
    __tablename__ = "dasdecs"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    ip_addr = db.Column(db.String(42), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(BLOB, nullable=False)
    sites = db.relationship('Site', backref='dasdecs', lazy=True)
    eas_tests = db.relationship('EAS', backref='dasdecs', lazy=True)


# Association table creating a many-to-many relationship between EAS and Site
eas_site_association = db.Table('eas_site_association',
                                db.Column('eas_id', db.Integer, db.ForeignKey('eas_tests.id')),
                                db.Column('site_id', db.Integer, db.ForeignKey('sites.id'))
                                )

class EAS(db.Model):
    """ Model for submitted EAS tests """
    __tablename__ = 'eas_tests'
    id = db.Column(db.Integer, primary_key=True)
    generated_id = db.Column(db.Integer, nullable=False)

    test_type = db.Column(db.String(12), nullable=False)    # RWT / RMT
    rx_from = db.Column(db.String(8), nullable=True)        # Where test came from
    originating = db.Column(db.Boolean, nullable=False)     # Test came from our station
    forwarded = db.Column(db.Boolean, nullable=False)       # Test received from another site

    started = db.Column(db.DateTime, nullable=False)
    ended = db.Column(db.DateTime, nullable=False)
    decoded_at = db.Column(db.DateTime, nullable=True)      # Null when originating
    sent_at = db.Column(db.DateTime, nullable=False)        # regardless of fwd or origin
    message = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    dasdec_id = db.Column(db.Integer, db.ForeignKey('dasdecs.id'), nullable=True)   # In event, DASDEC unavailable NULL
    sites = db.relationship('Site', secondary=eas_site_association, backref='eas_tests', lazy=True)

    # TODO Replace with Marshmallow Schema

#     def to_dict(self):
#         if self.originating:
#             return dict(
#                 id=self.id,
#                 originating=True,
#                 test_type=self.test_type,
#                 tx_timestamp=self.tx_timestamp,
#                 sites=[site.site_name for site in self.sites]
#             )
#         else:
#             return dict(
#                 id=self.id,
#                 originating=False,
#                 test_type=self.test_type,
#                 rx_from=self.rx_from,
#                 rx_timestamp=self.rx_timestamp,
#                 tx_timestamp=self.tx_timestamp,
#                 sites=[site.site_name for site in self.sites]
#             )
