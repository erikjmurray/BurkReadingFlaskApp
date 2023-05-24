"""
ArcPlus class definition
Reference to make API calls to Burk unit
Can use to add extensions info to database by Pickling this object
"""

import json
import requests
from dataclasses import field, dataclass


@dataclass
class ArcPlus:
    ip: str
    api_key: str
    url: str = field(init=False)

    def __post_init__(self):
        """ Create params after instantiation """
        self.url = f"http://{self.ip}/api.cgi"

    # ----- API CALLS-----
    def get_data(self, action):
        """Make request to Burk for JSON data of specific type"""
        params = {
            "action": action,
            "token": self.api_key
        }

        try:
            response = requests.get(self.url, params=params)
            if response.status_code == 200:
                data = json.loads(response.text)
                return data[action]
        except Exception as err:
            print(f'Error connecting {self.ip}')
            return None


    def get_meters(self) -> list:
        """Get meter data"""
        data = self.get_data('meter')
        if not data:
            return []
        return data

    def get_status(self) -> list:
        """Get Status data"""
        data = self.get_data('status')
        if not data:
            return []
        return data
