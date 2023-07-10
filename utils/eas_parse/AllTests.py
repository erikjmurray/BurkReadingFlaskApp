""" Stores a list of sorted EAS Tests """
from EasTest import EasTest
from dataclasses import dataclass, field
from typing import List

@dataclass
class AllTests:
    dasdec_name: str = ""
    originated_tests: List[EasTest] = field(default_factory=list)
    forwarded_tests: List[EasTest] = field(default_factory=list)
    decoded_tests: List[EasTest] = field(default_factory=list)
    eas_net_decoded_tests: List[EasTest] = field(default_factory=list)
    cap_eas_decoded_tests: List[EasTest] = field(default_factory=list)
