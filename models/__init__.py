"""
Models dir creates table models for SQL database
When imported to the app file they get created automatically
"""

from models.channels import Channel, MeterConfig, StatusOption
from models.readings import Reading, ReadingValue, Message, EAS
from models.site import Site
from models.user import User

from models.schemas import UserCreationSchema

