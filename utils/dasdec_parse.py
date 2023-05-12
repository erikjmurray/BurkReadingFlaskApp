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
    decoded_timestamp: Optional[str] = None
    originated_timestamp: Optional[str] = None
    locations: Optional[List[str]] = None


@dataclass
class AllTests:
    originated_tests: List[Test] = field(default_factory=list)
    forwarded_tests: List[Test] = field(default_factory=list)
    decoded_tests: List[Test] = field(default_factory=list)
    eas_net_decoded_tests: List[Test] = field(default_factory=list)
    cap_eas_decoded_tests: List[Test] = field(default_factory=list)


class DasdecLogParser:
    def __init__(self, content: str):
        self.content = content
        self.header_flag = False
        self.all_tests = AllTests()
        self.current_test = None
        self.current_list = []

        self.header_pattern = re.compile(r"----------------------------------------------------------------------")
        self.origination_pattern = re.compile(r'(?<=dasdec_)(.*?)(?=_events)')
        self.test_pattern = re.compile(r"(\d{0,4}):\t([A-Z]{3})\t([^\t]+)\t+'([^']*)'\s*\(([^)]*)\)\s*ORG=([A-Z]{3})")
        self.datetime_pattern = re.compile(r'(\b\w{3} \w{3} (?:\d{2}| \d{1}) \d{2}:\d{2}:\d{2} \d{4} \w{3}\b)')
        self.location_pattern = re.compile(r"\w+(?:\s+\w+){0,3}(?:,?\s[a-zA-Z]{2,})?,?\s[a-zA-Z]{2,}\(\d{6}\)")

    def parse_content(self) -> AllTests:
        for line in self.content.split('\n'):
            header_flag = self._check_header(line)
            if header_flag:
                event = self._parse_origination(line)
                if event:
                    self.current_list = getattr(self.all_tests, f"{event}_tests")
                    self._append_current_test()
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
        line = line.strip().replace('\t', '')
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
        else:
            if line.replace(' ', '').replace('\t', '') != '':
                print('Unmatched line:', line)


def read_from_file(filename) -> str:
    """ Given filename load data """
    with open(filename, 'r') as f:
        content = f.read()
    return content


def parse_dasdec_log():
    eas_log_dir = os.path.join('..', 'eas_logs')
    files = os.listdir(eas_log_dir)
    for file in files:
        content = read_from_file(os.path.join(eas_log_dir, file))
        all_tests = DasdecLogParser(content).parse_content()
        # for test in all_tests.originated_tests:
        #     print('\n-----------\n')
        #     print(test)
    print('Content parsed')


if __name__ == "__main__":
    parse_dasdec_log()
