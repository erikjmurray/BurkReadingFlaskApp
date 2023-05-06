""" Details Site model and schema """
# ----- 3RD PARTY IMPORTS -----
from sqlalchemy import BLOB
# ----- PROJECT IMPORTS -----
from extensions import db


class Site(db.Model):
    """
    Top level site config
    # NOTE: Site.eas_tests will return any EAS Tests associated with the Site
    """
    __tablename__ = "sites"
    id = db.Column(db.Integer, primary_key=True)
    ip_addr = db.Column(db.String(42), nullable=False)
    site_name = db.Column(db.String(20), nullable=False)
    api_key = db.Column(BLOB, nullable=False)
    site_order = db.Column(db.Integer, unique=True, nullable=False)
    channels = db.relationship('Channel', backref='site', lazy=True)

    def __init__(self, site_name, ip_addr, api_key):
        self.site_name = site_name
        self.ip_addr = ip_addr
        self.api_key = api_key
        self.site_order = self.get_next_site_order()

    def get_next_site_order(self):
        max_site_order = Site.query.with_entities(db.func.max(Site.site_order)).scalar()
        if max_site_order is None:
            return 0
        else:
            return max_site_order + 1

    @property
    def display_name(self):
        return self.site_name.replace('_', ' ')

    def __repr__(self):
        return f"Site {self.site_name}"
