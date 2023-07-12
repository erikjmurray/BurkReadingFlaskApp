""" Functions for parsing HTML from DASDEC """
# --- BUILT-IN IMPORTS ---
from typing import List, Tuple

# --- PROJECT IMPORTS ---
from utils.eas_parse.DasdecPageParser import DasdecPageParser


def run_parser(result: str) -> dict:
    """ Sort raw html into usable content """
    parser = DasdecPageParser()
    parsed_data = parser.parse(result)

    return parsed_data


def parse_eas_data(results: List[Tuple[int, str]]) -> List[Tuple[int, str]]:
    """ Call parser on scraped data """
    eas_data = []
    for code, content in results:
        if code == 200:
            eas_data.append((code, run_parser(content)))    # NOTE: run parser returns dict
        else:
            eas_data.append((code, content))
    return eas_data

    # skipped_tests = ['FFW', 'FFA', 'FLW', 'FLA', 'SMW', 'SVR', 'SVA', 'TOR']
    # for key in parsed_data.keys():
    #     print("\n\n\n$$$$$$$$$$$$$$$$$\n", key.upper(), "\n$$$$$$$$$$$$$$$$$\n")
    #     for item in parsed_data[key]:
    #         if item['EAS'] in skipped_tests:
    #             continue
    #         print("\n------------------")
    #         for k, v in item.items():
    #             print(f"{k}: {v}")
    # return

