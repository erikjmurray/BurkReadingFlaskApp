""" Functions for parsing HTML from DASDEC """
# --- PROJECT IMPORTS ---
from utils.eas_parse.DasdecPageParser import DasdecPageParser


def parse(result: str) -> None:
    """ Sort raw html into usable content """
    parser = DasdecPageParser()
    parsed_data = parser.parse(result)
    for key in parsed_data.keys():
        print("\n\n\n$$$$$$$$$$$$$$$$$\n", key.upper(), "\n$$$$$$$$$$$$$$$$$\n")
        for item in parsed_data[key]:
            print("\n------------------")
            for k, v in item.items():
                print(f"{k}: {v}")
    return
