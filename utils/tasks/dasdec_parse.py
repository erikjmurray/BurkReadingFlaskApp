import os
import re
from dataclasses import dataclass, field
from typing import List, Match, Optional


@dataclass
class Test:
    id: str
    test_type: str
    full_test_type: str
    ipaws: str
    organization: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    delivered_timestamp: Optional[str] = None
    locations: Optional[List[str]] = None


class AllTests:
    def __init__(self, dasdec_name):
        self.dasdec_name = dasdec_name
        self.originated_tests = []
        self.forwarded_tests = []
        self.decoded_tests = []
        self.eas_net_decoded_tests = []
        self.cap_eas_decoded_tests = []


class DasdecLogParser:
    def __init__(self, content: str, dasdec_name: str):
        self.content = content
        self.header_flag = False
        self.all_tests = AllTests(dasdec_name=dasdec_name)
        self.current_test = None
        self.current_list = []

        self.header_pattern = re.compile(r"----------------------------------------------------------------------")
        self.origination_pattern = re.compile(r'(?<=dasdec_)(.*?)(?=_events)')
        self.test_pattern = re.compile(r"(\d{0,6}):\t([A-Z]{3})\t([^\t]+)\t+'([^']*)'\s*\(((?:[^)]|\([^)]*\))*)\)\s*ORG=([A-Z]{3})")
        self.datetime_pattern = re.compile(r'(\b\w{3} \w{3} (?:\d{2}| \d{1}) \d{2}:\d{2}:\d{2} \d{4} \w{3}\b)')
        self.location_pattern = re.compile(r'\b.*?\(\d+\)')

    def parse_content(self) -> AllTests:
        for line in self.content.split('\n'):
            header_flag = self._check_header(line)
            if header_flag:
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
        header_match = self.header_pattern.search(line)
        if header_match:
            self.header_flag = not self.header_flag
        return self.header_flag

    def _parse_origination(self, line: str) -> Optional[str]:
        origination_match = self.origination_pattern.search(line)
        if origination_match:
            return origination_match.group(1)
        return None

    def _append_current_test(self) -> None:
        if self.current_test:
            self.current_list.append(self.current_test)
            self.current_test = None
        return

    def _match_test(self, line: str) -> Optional[Match]:
        return self.test_pattern.search(line)

    def _create_new_test(self, test_match: Match) -> Test:
        return Test(
            id=test_match.group(1),
            test_type=test_match.group(2),
            full_test_type=test_match.group(3),
            ipaws=test_match.group(4),
            organization=test_match.group(5),
        )

    def _parse_test_data(self, line: str) -> None:
        datetime_match = self.datetime_pattern.findall(line)
        location_match = self.location_pattern.findall(line)

        if datetime_match:
            if len(datetime_match) > 1:
                self.current_test.start_time = datetime_match[0]
                self.current_test.end_time = datetime_match[1]
            else:
                if any(keyword in line for keyword in ['Decoded', 'Originated', 'Forwarded']):
                    self.current_test.delivered_timestamp = datetime_match[0]
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


def read_from_file(filename: str) -> str:
    """ Given filename load data """
    with open(filename, 'r') as f:
        content = f.read()
    return content


def get_dasdec_name_from_file_name(file: str) -> str:
    pattern = r'^\d{8}_\d{4}_([^_]+)_'
    match = re.match(pattern, file)

    if match:
        return match.group(1)


def parse_dasdec_logs() -> List[AllTests]:
    """
    Grabs all files in EAS LOGS folder and parses data into lists of tests
    """
    eas_log_dir = os.path.join(os.getcwd(), 'eas_logs')
    files = os.listdir(eas_log_dir)

    all_eas_data = []
    for file in files:
        content = read_from_file(os.path.join(eas_log_dir, file))
        dasdec_name = get_dasdec_name_from_file_name(file)
        all_tests = DasdecLogParser(content, dasdec_name).parse_content()
        # id of decoded test is the same as forwarded test.
        # sort and return only pertinent tests
        # orig, fwd, decoded(received)
        # note logs only include expired events
        test_func(all_tests)
        all_eas_data.append(all_tests)
    return all_eas_data


def test_func(all_tests: AllTests):
    forwarded_ids = [test.id for test in  all_tests.forwarded_tests]
    decoded_ids = [test.id for test in all_tests.decoded_tests]
    cap_ids = [test.id for test in all_tests.cap_eas_decoded_tests]
    net_ids = [test.id for test in all_tests.eas_net_decoded_tests]

    for test in forwarded_ids:
        if test in decoded_ids:
            print(f'Test {test} forwarded from Decoded')
        elif test in cap_ids:
            print(f'Test {test} forwarded from CAP')
        elif test in net_ids:
            print(f'Test {test} forwarded from NET')
        else:
            print(f'Where did test {test} come from?')

