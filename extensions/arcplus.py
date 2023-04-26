"""
ArcPlus class definition
Reference to make API calls to Burk unit
Can use to add extensions info to database by Pickling this object
"""

import json
import httpx
import asyncio
from dataclasses import field, dataclass

@dataclass
class ArcPlus:
    ip: str
    api_key: str
    url: str = field(init=False)
    # req_meters: List = field(default_factory=List)
    # req_status: List = field(default_factory=List)
    # salt: str = ""

    def __post_init__(self):
        """ Create params after instantiation """
        self.url = f"http://{self.ip}/api.cgi"

    # -----ASYNCHRONOUS API CALLS-----
    async def async_get_data(self, action):
        """Make request to Burk for JSON data of specific type"""
        params = {
            "action": action,
            "token": self.api_key
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(self.url, params=params)
                data = json.loads(resp.text)
                return data[action]
            except:
                return None

    async def async_get_meters(self) -> list:
        """Get meter data async"""
        data = await self.async_get_data('meter')
        if not data:
            return []
        return data

    async def async_get_status(self) -> list:
        """Get Status data async"""
        data = await self.async_get_data('status')
        if not data:
            return []
        return data

    async def get_meters_and_status(self):
        meters, statuses = await asyncio.gather(
            self.async_get_meters(),
            self.async_get_status()
        )
        return meters, statuses

    # # -----SYNCHRONOUS API CALLS-----
    # def get_data(self, action):
    #     """Make request to Burk for JSON data of specific type"""
    #     params = {
    #         "action": action,
    #         "token": self.api_key
    #     }
    #     with httpx.Client() as client:
    #         try:
    #             resp = client.get(self.url, params=params)
    #             # return resp
    #             data = json.loads(resp.text)
    #             return data[action]
    #         except:
    #             return None
    #
    # def get_meters(self) -> list:
    #     """Get meter data"""
    #     data = self.get_data('meter')
    #     if not data:
    #         return []
    #     return data
    #
    # def get_status(self):
    #     """Get status data"""
    #     data = self.get_data('status')
    #     if not data:
    #         return []
    #     return data

