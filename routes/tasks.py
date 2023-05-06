"""
Executes tasks such as PDF generation
"""
# ----- 3RD PARTY IMPORTS -----
from flask import Blueprint, make_response, Response
from reportlab.platypus import (BaseDocTemplate, Frame, Image, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Table)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import legal, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
# ----- BUILT IN IMPORTS ----
from datetime import datetime, timedelta
from io import BytesIO
from typing import Tuple, List, Optional
# ----- PROJECT IMPORTS -----
from models import EAS, Channel, Reading, Site
from utils import get_valid_readings


# create Blueprint object
tasks = Blueprint('tasks', __name__)


@tasks.route('/<int:site_id>/<start_date>/<end_date>')
def generate_pdf(site_id: int,
                 start_date: str,
                 end_date: str) -> Response:
    """ Route to initiate PDF report of site readings for a date range """
    site = Site.query.get(site_id)

    # convert from string format to datetime format
    date_range = (input_dates_to_datetime(start_date), input_dates_to_datetime(end_date))
    pdf_data = create_pdf(site, date_range)

    # Create response object
    response = make_response(pdf_data)
    response.headers.set('Content-Type', 'application/pdf')
    # indexing removes hh:mm:ss
    filename = f"{start_date[:-9]}_to_{end_date[:-9]}_{site.site_name}_report.pdf"
    response.headers.set('Content-Disposition', 'attachment', filename=filename)

    return response


def input_dates_to_datetime(date_string: str) -> datetime:
    """ Converts string date input to datetime object """
    date_format = '%Y-%m-%d %H:%M:%S'
    date_as_datetime_obj = datetime.strptime(date_string, date_format)
    return date_as_datetime_obj


def create_pdf(site: Site,
               date_range: Tuple[datetime, datetime]) -> bytes:
    """ Create pdf of site readings """
    # create pdf document
    buffer = BytesIO()
    doc = create_pdf_document(buffer)
    styles = define_styles()

    # Gather all dates from start date up to end date
    dates = create_list_of_individual_dates(*date_range)

    # Define common elements of each page
    date_range_subheader = f'{date_range[0].strftime("%B %d, %Y")} - {date_range[1].strftime("%B %d, %Y")}'
    report_data = dict(
        title=Paragraph(f'<u>{site.site_name.replace("_", " ")} Report</u>', styles['title']),
        subheader=Paragraph(date_range_subheader, styles['subheader']),
        styles=styles
    )

    # Define dataframe headers
    readings_headers = ['Timestamp'] + [channel.title for channel in site.channels] + ['MCEOD']
    message_headers = ['Timestamp', 'Messages', 'User Notes']

    report = []
    for i, date in enumerate(dates):
        # Query database for data on a given date
        readings_for_date = query_readings_by_date(date)
        readings_data_for_date = get_valid_readings(readings_for_date, site)

        # create table of readings on specific date
        readings_df = create_readings_dataframe(readings_headers, readings_data_for_date)
        readings_table = create_table_from_readings_dataframe(readings_df, styles, site.channels)

        # Gather message data from database
        message_df = create_message_dataframe(message_headers, readings_data_for_date)

        # Remove rows from dataframe if no input. If no rows, do not create blank page of messages.
        message_df = remove_df_rows_w_no_data(['Messages', 'User Notes'], message_df)

        # create page data for the current date
        report_data['current_date'] = date
        report_for_date = build_report_for_date(report_data, readings_table, message_df)
        report += report_for_date

        # TODO: Move this after EAS Report
        # If last page of readings, change template otherwise start a new page
        apply_histogram_formatting = [NextPageTemplate('figure'), PageBreak()]
        report += apply_histogram_formatting if i == (len(dates) - 1) else [PageBreak()]

    # TODO: Implement report page with EAS Tests
    # Add EAS page with same formatting as report
    eas_report = build_eas_report(site, date_range)
    # report += eas_report
    #
    # # Applies page formatting for the histogram
    # report += [NextPageTemplate('figure'), PageBreak()]

    # Add time series data of meter channels to report
    histogram = build_histogram(site, date_range)
    if histogram:
        report += [
            figure_to_image(histogram)
        ]

    # Create document with settings at pdf_path location
    doc.build(report)
    pdf_data = buffer.getvalue()
    return pdf_data


# ----- DOCUMENT SETUP -----
def create_pdf_document(pdf_path: BytesIO) -> BaseDocTemplate:
    """ Build the document object with templates """
    # Create Templates
    templates = define_templates()

    # Create document
    pdf_doc = BaseDocTemplate(
        pdf_path,
        pageTemplates=templates,
    )
    return pdf_doc


def define_templates() -> List[PageTemplate]:
    """ Create templates for the document """
    # define onPage functions
    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        canvas.drawString(40, 20, f"Page {page_num}")

    def add_approval(canvas, doc):
        canvas.setFont('Helvetica-Bold', 16)
        approved = "Approved by: __________________________"
        canvas.drawString(8.75 * inch, 20, approved)

    padding = dict(
        leftPadding=40,
        rightPadding=40,
        topPadding=24,
        bottomPadding=30)

    page_size = landscape(legal)

    # define frames
    padded_frame = Frame(0, 0, *page_size, **padding, )
    fullpage_frame = Frame(0, 0, *page_size)

    base_template = PageTemplate(
        id='base',
        frames=padded_frame,
        pagesize=page_size,
        onPage=add_page_number,
        onPageEnd=add_approval
    )

    figure_template = PageTemplate(
        id='figure',
        frames=fullpage_frame,
        pagesize=page_size,
        onPage=add_page_number
    )

    return [base_template, figure_template]


def define_styles() -> dict:
    """ Define styles for the document """
    # get general styles
    styles = getSampleStyleSheet()

    # create custom styles
    title = ParagraphStyle(name='custom_title', parent=styles['Heading1'], alignment=1, spaceAfter=0)
    subheader = ParagraphStyle(name='subheader', parent=styles['Heading2'], alignment=1, spaceBefore=-10)
    table_title = ParagraphStyle(name='table_title', parent=styles['Heading2'], fontSize=14, spaceBefore=-5,
                                 spaceAfter=5)
    table_headers = ParagraphStyle(name='table_headers', parent=styles['Heading2'], fontSize=12, alignment=1)
    table_data = ParagraphStyle(name='table_data', parent=styles['Normal'], alignment=1, wordWrap='LTR')
    foot_note = ParagraphStyle(name='foot_note', parent=styles['Heading2'], alignment=1, spaceAbove=50)
    bullet_style = ParagraphStyle(name='bullets', parent=table_data, alignment=0, leftIndent=5)

    styles_to_add = [title, subheader, table_title, table_headers, table_data, foot_note, bullet_style]
    for item in styles_to_add:
        styles.add(item)
    return styles


def create_list_of_individual_dates(start_date: datetime,
                                    end_date: datetime) -> List[datetime]:
    """ Get a list of datetime objects in a given range """
    dates = []
    while start_date <= end_date:
        dates.append(start_date)
        start_date += timedelta(days=1)
    return dates


# ----- SQL Queries -----
def query_readings_by_date(date: datetime) -> List[Reading]:
    """ Queries SQL that match a specific date """
    # if timestamp between 00:00:00:00.. and 23:59:59:99.. return data
    start_datetime = datetime.combine(date, datetime.min.time())
    end_datetime = datetime.combine(date, datetime.max.time())
    readings = Reading.query.filter(Reading.timestamp >= start_datetime, Reading.timestamp <= end_datetime).all()

    return readings


def query_readings_by_date_range(dates: Tuple[datetime, datetime]) -> List[Reading]:
    """ Queries SQL for a range of dates worth of readings """
    readings = Reading.query.filter(Reading.timestamp >= dates[0], Reading.timestamp <= dates[1]).all()
    return readings


def query_eas_tests_by_date_range(site: Site,
                                  dates: Tuple[datetime, datetime]) -> List[EAS]:
    """ Queries SQL for EAS Tests transmitted on the site for a specific range of dates """
    eas_tests = EAS.query.join(EAS.sites).filter(
        Site.id == site.id,
        EAS.tx_timestamp >= dates[0],
        EAS.tx_timestamp <= dates[1]
    ).order_by(
        EAS.tx_timestamp.asc()
    ).all()
    return eas_tests


# ----- PANDAS DATAFRAME CREATION -----
def create_readings_dataframe(headers: List[str],
                              readings: List[dict]) -> pd.DataFrame:
    """  Create pandas dataframe for Readings PDF """
    rows = []
    for row in readings:
        timestamp = row.get('timestamp').strftime("%m/%d/%Y, %H:%M")
        channel_values = []
        for value in row.get('reading_values'):
            try:
                value = float(value)
                channel_values.append(value)
            except ValueError:
                channel_values.append(value)
        mceod = row.get('user')
        reading_data = [timestamp] + channel_values + [mceod]
        rows.append(reading_data)

    return pd.DataFrame.from_records(rows, columns=headers)


def create_message_dataframe(headers: List[str],
                             readings: List[dict]) -> pd.DataFrame:
    """ Create pandas dataframe for Message page """
    rows = []
    for row in readings:
        # Adding * and index[0] blank to force formatting in format_df_rows()
        messages = '*'.join([' '] + row.get('messages'))
        notes = '*'.join([' '] + [row.get('notes')])
        timestamp = row.get('timestamp').strftime("%m/%d/%Y, %H:%M")

        reading_data = [timestamp, messages, notes]
        rows.append(reading_data)

    return pd.DataFrame.from_records(rows, columns=headers)


def remove_df_rows_w_no_data(headers: List[str],
                             df: pd.DataFrame) -> pd.DataFrame:
    """ Given known headers removes row if all header = None """
    # replace empty string with numpy NaN none type
    for header in headers:
        df[header].replace('', np.nan, inplace=True)
    # if all header = NaN, delete row
    df = df.dropna(subset=headers, how='all')
    return df


# ----- REPORTLAB TABLE CREATION -----
def create_table_from_readings_dataframe(df: pd.DataFrame,
                                         styles: dict,
                                         channels: List[Channel]) -> Table:
    """ Create a ReportLab table object from the dataframe """
    # Adds to table data
    columns = [Paragraph(col, styles['table_headers']) for col in df.columns]
    rows = format_df_rows(df, styles, channels)

    table_data = [columns] + rows
    table_style = [
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.lightgrey, colors.white]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('WORDWRAP', (0, 0), (-1, -1), 1)
    ]

    return Table(table_data, style=table_style, hAlign='LEFT')


def create_table_from_messages_dataframe(df: pd.DataFrame,
                                         styles: dict) -> Table:
    """ Create a ReportLab table object from the dataframe """
    # Adds to table data
    columns = [Paragraph(col, styles['table_headers']) for col in df.columns]
    rows = format_df_rows(df, styles, channels=None)

    table_data = [columns] + rows
    table_style = [
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.lightgrey, colors.white]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # ALIGNS HEADERS CENTER
        ('VALIGN', (1, 1), (-1, -1), 'TOP'),    # ALIGNS MESSAGES AND NOTES TOP
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('WORDWRAP', (0, 0), (-1, -1), 1)
    ]

    return Table(table_data, style=table_style, hAlign='LEFT')


def format_df_rows(df: pd.DataFrame,
                   styles: dict,
                   channels: Optional[List[Channel]]) -> List:
    rows = []
    for row_i, row in df.iterrows():
        table_row = []
        # apply styling to the cell depending on the value/value type
        for val_i, value in enumerate(row.values):
            if type(value) == float:
                if val_i == 0 or val_i > len(channels):
                    raise IndexError    # either more data before channels or timestamp flagged as float
                meter_style = check_meter_limits_apply_bg_color(value, channels[val_i - 1], styles['table_data'])
                cell = Paragraph(str(value), meter_style)
            elif '*' in value:
                value = '*'.join(value.split('*')[1:])
                bullets = value.replace('*', '<br/>')
                cell = Paragraph(bullets, styles['bullets'])
            else:
                cell = Paragraph(value, styles['table_data'])

            table_row.append(cell)
        rows.append(table_row)
    return rows


def check_meter_limits_apply_bg_color(meter_value: float,
                                      channel: Channel,
                                      cell_style: ParagraphStyle) -> ParagraphStyle:
    if meter_value >= channel.meter_config[0].upper_limit:
        meter_style = ParagraphStyle('above_upper', parent=cell_style, backColor=channel.meter_config[0].upper_lim_color)
    elif meter_value <= channel.meter_config[0].lower_limit:
        meter_style = ParagraphStyle('below_lower', parent=cell_style, backColor=channel.meter_config[0].lower_lim_color)
    else:
        meter_style = cell_style
    return meter_style


# ----- BUILD PDF PAGES -----
def build_report_for_date(report_data: dict,
                          readings: Table,
                          messages: pd.DataFrame) -> list:
    """ Build a ReportLab page using database query data of specific date """
    # init passed settings
    date = report_data.get('current_date')
    title = report_data.get('title')
    subheader = report_data.get('subheader')
    styles = report_data.get('styles')

    report_for_date = []
    # build readings page
    report_for_date += [
        title,
        subheader,
        Paragraph(f'Readings for {date.strftime("%B %d, %Y")}', styles['table_title']),
        readings,
    ]
    # add messages, user notes, and EAS information if available
    if not messages.empty:
        message_table = create_table_from_messages_dataframe(messages, styles)

        report_for_date += [
            PageBreak(),
            # On new page display user notes and auto generated messages
            title, subheader,
            Paragraph(f'Notes for {date.strftime("%B %d, %Y")}', styles['table_title']),
            message_table,
        ]
    else:
        report_for_date += [
            Paragraph('There were no auto-generated messages or user notes on this day', styles['foot_note']),
        ]
    return report_for_date


def build_eas_report(site: Site,
                     date_range: Tuple[datetime, datetime]) -> List:
    """ Create a page in the report detailing the EAS test sent and received """
    eas_tests = query_eas_tests_by_date_range(site, date_range)
    eas_df = create_eas_dataframe([eas_test.to_dict() for eas_test in eas_tests])
    print(eas_df.to_string())
    return []


def create_eas_dataframe(eas_tests: List[EAS]) -> pd.DataFrame:
    return pd.DataFrame(eas_tests)


# ----- BUILD HISTOGRAM OF VALUES OF DATERANGE -----
def build_histogram(site: Site,
                    date_range: Tuple[datetime, datetime]) -> Optional[Figure]:
    """ Gather data and create histogram of meter readings over input dates range """
    # get database data
    readings_for_date_range = query_readings_by_date_range(date_range)
    data_by_input_date_range = get_valid_readings(readings_for_date_range, site)
    # if there is no data for the readings in the specified range, do not create histogram
    if not data_by_input_date_range:
        return None

    # create table of readings on specific date
    headers = ['Timestamp'] + [channel.title for channel in site.channels] + ['MCEOD']
    input_date_range_df = create_readings_dataframe(headers, data_by_input_date_range)
    # remove_df_rows_w_no_data(input_date_range_df, headers[1:-1])

    # headers does not include Timestamp as Timestamp is x axis reading.
    histogram = create_histogram_of_readings(input_date_range_df, date_range, headers[1:-1])
    return histogram


def create_histogram_of_readings(df: pd.DataFrame,
                                 dates: Tuple[datetime, datetime],
                                 meter_channels: List[str]) -> Figure:
    """ Plot readings data over time as line graph """
    # Datetime objects for x-axis
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df.set_index('Timestamp', inplace=True)

    # define figure and add data
    fig = Figure(figsize=(14, 7.5))
    ax = fig.add_subplot(1, 1, 1)
    df[meter_channels].plot(ax=ax)

    # x axis tick marks
    x_ticks = pd.date_range(dates[0], dates[1], freq='D')
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([x.strftime('%Y-%m-%d') for x in x_ticks], rotation=45)
    ax.set_xlim(dates[0], dates[1])

    # set labels
    ax.set_ylabel('Values')
    ax.set_title('Histogram of Meter Readings')

    # adjust positioning
    ax.legend(loc='upper right')
    # fig.subplots_adjust(left=0.1)
    return fig


def figure_to_image(fig: Figure) -> Image:
    buffer = BytesIO()
    fig.savefig(buffer, format='png', dpi=300)
    buffer.seek(0)
    x, y = fig.get_size_inches()
    return Image(buffer, x * inch, y * inch)
