""" Details DASDEC model """
# ----- 3RD PARTY IMPORTS -----
from sqlalchemy import BLOB

# ----- PROJECT IMPORTS -----
from extensions import db


class Dasdec(db.Model):
    """ Mode for DASDEC data """
    __tablename__ = "dasdecs"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    ip_addr = db.Column(db.String(42), nullable=False)
    password = db.Column(BLOB, nullable=False)
    # operational_area = db.Column(db.String(2), nullable=False)      # TODO: By State or Regional Area?
    sites = db.relationship('Site', backref='dasdec', lazy=True)
    eas_tests = db.relationship('EAS', backref='dasdec', lazy=True)

# TODO: Decide if EAS Tests should maintain a relationship to Site directly.
# Association table creating a many-to-many relationship between EAS and Site
# eas_site_association = db.Table('eas_site_association',
#                                 db.Column('eas_id', db.Integer, db.ForeignKey('eas_tests.id')),
#                                 db.Column('site_id', db.Integer, db.ForeignKey('sites.id'))
#                                 )

class EAS(db.Model):
    """ Model for submitted EAS tests """
    __tablename__ = 'eas_tests'
    id = db.Column(db.Integer, primary_key=True)
    # TODO: Reconsider fields
    # test_type = db.Column(db.String(10), nullable=False)
    # tx_type = # TODO: define string that relates to origination or forwarding.
    # rx_from = db.Column(db.String(50), nullable=True)
    # rx_timestamp = db.Column(db.DateTime, nullable=True)
    # tx_timestamp = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    dasdec_id = db.Column(db.Integer, db.ForeignKey('dasdecs.id'), nullable=False)
    # sites = db.relationship('Site', secondary=eas_site_association, backref='eas_tests', lazy=True)

# # TODO Replace with Marshmallow Schema

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
