""" Stores EAS Test data """
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class EasTest:
    id: int
    test_type: str
    full_test_type: str
    ipaws: str
    organization: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    delivered_timestamp: Optional[str] = None
    locations: Optional[List[str]] = None
