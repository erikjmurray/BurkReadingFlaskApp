"""
Models dir creates table models for SQL database
When imported to the app file they get created automatically
"""

from models.channels import Channel, MeterConfig, StatusOption
from models.readings import Reading, ReadingValue, Message
from models.dasdec import Dasdec, EAS, eas_site_association
from models.site import Site
from models.user import User

