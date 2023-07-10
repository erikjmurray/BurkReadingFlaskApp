""" Dasdec Log Parser Object """
# --- BUILT-IN IMPORTS ---
import re
from typing import Match, Optional
# --- PROJECT IMPORTS ---
from utils.eas_parse.AllTests import AllTests
from utils.eas_parse.EasTest import EasTest

class DasdecLogParser:
    def __init__(self, content: str):
        self.content = content
        self.header_flag = False
        self.all_tests = AllTests()
        self.current_test = None
        self.current_list = []

        self.header_pattern = re.compile(r"----------------------------------------------------------------------")
        self.origination_pattern = re.compile(r'(?<=dasdec_)(.*?)(?=_events)')
        self.test_pattern = re.compile(r"(\d{0,6}):\t([A-Z]{3})\t([^\t]+)\t+'([^']*)'\s*\(((?:[^)]|\([^)]*\))*)\)\s*ORG=([A-Z]{3})")
        self.datetime_pattern = re.compile(r'(\b\w{3} \w{3} (?:\d{2}| \d{1}) \d{2}:\d{2}:\d{2} \d{4} \w{3}\b)')
        self.location_pattern = re.compile(r'\b.*?\(\d+\)')


    def parse_content(self) -> AllTests:
        """ Sorts log data into usable classes """
        for line in self.content.split('\n'):
            self._check_header(line)
            if self.header_flag:
                event = self._parse_origination(line)
                if event:
                    self._append_current_test()
                    self.current_list = getattr(self.all_tests, f"{event}_tests")
                continue

            test_match = self._match_test(line)
            if test_match:
                self._append_current_test()
                self.current_test = self._create_new_test(test_match)
            else:
                self._parse_test_data(line)
        self._append_current_test()
        return self.all_tests
    

    def _check_header(self, line: str) -> bool:
        """ Flags line as header material """
        header_match = self.header_pattern.search(line)
        if header_match:
            self.header_flag = not self.header_flag
        return self.header_flag
    

    def _parse_origination(self, line: str) -> Optional[str]:
        """ Attempts to match origination pattern """
        origination_match = self.origination_pattern.search(line)
        if origination_match:
            return origination_match.group(1)
        return None
    

    def _append_current_test(self) -> None:
        """ Append current test to working list and reset test """
        if self.current_test:
            self.current_list.append(self.current_test)
            self.current_test = None
        return
    

    def _match_test(self, line: str) -> Optional[Match]:
        """ """
        return self.test_pattern.search(line)
    

    def _create_new_test(self, test_match: Match) -> EasTest:
        """ Initialize new test object """
        return EasTest(
            id=test_match.group(1),
            test_type=test_match.group(2),
            full_test_type=test_match.group(3),
            ipaws=test_match.group(4),
            organization=test_match.group(5),
        )

    def _parse_test_data(self, line: str) -> None:
        """ Sorts Datetime and Location data into proper fields """
        datetime_match = self.datetime_pattern.findall(line)
        location_match = self.location_pattern.findall(line)

        if datetime_match:
            if len(datetime_match) > 1:
                self.current_test.start_time = datetime_match[0]
                self.current_test.end_time = datetime_match[1]
            else:
                if 'Decoded' in line:
                    self.current_test.decoded_timestamp = datetime_match[0]
                elif 'Originated' in line:
                    self.current_test.originated_timestamp = datetime_match[0]
        elif location_match:
            if not self.current_test.locations:
                self.current_test.locations = []
            self.current_test.locations.extend(location_match)
        # else:
        #     if line.replace(' ', '').replace('\t', '') == '':
        #         return
        #     if line == '----------------------------------------------------------------------' \
        #        or line == '++++++++++++++++++++++++++++++++++++++++++++++':
        #         return
        #     if 'for this time period.' in line \
        #         or 'Expired originated/forwarded alerts:' in line:
        #         return
        #     print('Unmatched line:', line)
        
