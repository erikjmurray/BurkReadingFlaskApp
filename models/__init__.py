"""
Models dir creates table models for SQL database
When imported to the app file they get created automatically
"""

from models.config import User, Site, Channel, MeterConfig, StatusOption
from models.readings import Reading, ReadingValue, Message, EAS

