""" Parser for HTML scraped from DASDEC Page """
from typing import List
from bs4 import BeautifulSoup, Tag, ResultSet
import re

class DasdecPageParser:
    def __init__(self, **kwargs):
        self.eas_data = {}
        self.counter = 0
        self.target = ""
        self.headers = []
        self.current_test = {}
        self.current_list = []

    def parse(self, content: str) -> dict:
        """ Given page HTML return usable data """
        self._init_eas_data()
        target_tables = self._get_eas_tables(content)

        for table_index, table in enumerate(target_tables):
            rows = self._parse_html(str(table), Tag(name='tr'))
            
            if table_index % 2 == 0:
                self._change_list()
            else:
                self._gather_data(rows)
            
        return self.eas_data

    def _init_eas_data(self) -> None:
        """ Resets EAS Data dict before parsing """
        self.eas_data = {
            "scheduled": [],
            "current": [],
            "expired": [],
            }
        return

    def _get_eas_tables(self, content: str) -> List[str]:
        """ Get HTML for tables with EAS Test Content """
        table_tag = Tag(name='table', attrs={'rules': 'cols'})
        full_page = self._parse_html(content, table_tag)

        page_tables = self._parse_html(str(full_page[1]), Tag(name='table'))

        return self._filter_page_tables(page_tables)

    def _parse_html(self, html: str, html_tag: Tag) -> ResultSet:
        """ Use BeautifulSoup to get specific elements from HTML """
        soup = BeautifulSoup(html, 'lxml')
        target_output = soup.find_all(html_tag.name, attrs=html_tag.attrs)
        return target_output

    def _filter_page_tables(self, tables):
        """ Only return pertinent tables """
        filtered_tables = []
        filter_items = ["", "RMT"]
        tables = [table for table in tables if table.text.strip() not in filter_items]
        
        for table in tables:
            if "alert records displayed" not in table.text.strip():
                filtered_tables.append(table)
                
        target_indexes = [0, 1, 2, 3, 4, 6]

        return [filtered_tables[i] for i in target_indexes]

    def _change_list(self) -> None:
        """ Reassigns target for EAS Data dependent on counter """       
        if self.counter == 0:
            self._assign_list("scheduled")
        elif self.counter == 1:
            self._assign_list("current")
        elif self.counter == 2:
            self._assign_list("expired")
        else:
            # Reset counter
            print("Reused parser object, not properly error checked. Proceed with caution.")
            self.counter = 0
            self._assign_list("scheduled")
        return

    def _assign_list(self, key: str) -> None:
        """ Set target key and increment counter """
        self.target = key
        self.counter += 1
        return

    def _gather_data(self, rows: List) -> None:
        """ Get Data for EAS Test """
        self.headers = self._get_headers(rows)

        rows = self._filter_rows(rows)

        for row_index, row in enumerate(rows):
            data = self._parse_row_data(row)

            if row_index % 2 == 0:
                data = self._filter_data(data)
                self._sort_eas_data(data)
            else:
                self._add_message(data)
                self._append_reset_cur_test()

        self.eas_data[self.target] = self.current_list
        self.current_list = []
        return

# TODO: REFACTOR
    def _get_headers(self, rows: List) -> List[str]:
        """ Grab headers from first row """
        headers = self._parse_html(str(rows[0]), Tag(name='td'))
        headers = [header.text.strip() for header in headers]
        key_map = {
            'EAS Type': 'EAS',
            'Start Time': 'Started',
            'End Time': 'Ended',
            'Location (Limit)': 'Locations',
            }
        filtered_headers = []
        for header in headers:
            if header in key_map.keys():
                filtered_headers.append(key_map[header])
            else:
                filtered_headers.append(header)
        return filtered_headers

    def _filter_rows(self, rows: List) -> List:
        """ Removes unnecessary rows """
        rows = rows[1:-1]   # headers and blank last
        rows = [row for row in rows if row.get('bgcolor') != "#CC33CC"]  # currently active alert
        rows = [row for row in rows if row.text.strip() not in ["", "RMT"]]  # blank and RMT
        return rows

    def _parse_row_data(self, row) -> List:
        """ Get data points for each td in row """
        data = self._parse_html(str(row), Tag(name="td"))
        return [datum.text.strip() for datum in data]
    
# TODO: BREAK INTO SMALLER FUNCTIONS
    def _sort_eas_data(self, data: List) -> None:
        """ Put EAS Data under associated headers """
        if len(data) < len(self.headers):
            return

        timestamp_format = r'(\w{3} \w{3} \d{2} \d{2}:\d{2}:\d{2} \d{4} \w{3})'
        for i, header in enumerate(self.headers):
            matches = re.findall(timestamp_format, data[i])

            if header == "Chnl/Orig":
                channel, origin = data[i].split('from')
                self.current_test['Channel'] = channel
                self.current_test['Origin'] = origin
            elif "Node" in data[i]:
                eas, node = data[i].split('Node:')
                self.current_test[header] = eas
                self.current_test['Node'] = node.strip().replace("'", '')
            elif header == "Locations":
                self.current_test[header] = data[i].split("\n")
            elif matches:
                self.current_test[header] = matches[0]
                if len(matches) > 1:
                    subheader = re.sub(timestamp_format, '', data[i]).strip()
                    subheader = subheader.replace(':', '')
                    self.current_test[subheader] = matches[1]
                if len(matches) > 2:
                    print("More matches")
            else:
                self.current_test[header] = data[i]
        return

    def _filter_data(self, data: List) -> List:
        """ Remove extra data point for RMT """
        return [item for item in data if item != "RMT"]
    
    def _add_message(self, data) -> None:
        """ Add EAS Message to EAS Data """
        message = data[0]
        message = message.replace('Decoded as: ', '')
##        message = message.replace('\n', ' ')
        # Removes audio alert links
        if 'Audio Portion' in message:
            message = message.split('Audio Portion')[0]
        if 'Pre-Alert Audio' in message:
            message = message.split('Pre-Alert Audio')[0]
        self.current_test["Message"] = message
        return

    def _append_reset_cur_test(self) -> None:
        """ Append test to list and reset test """
        self.current_list.append(self.current_test)
        self.current_test = {}
        return
