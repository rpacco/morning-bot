import httpx
import pandas as pd
from datetime import datetime
import json
from bs4 import BeautifulSoup
import ast
from google.cloud import logging as gcp_logging
import ssl


def _get_client(logger: gcp_logging.Logger):
    try:
        logger.log_text("Getting HTTP client", severity="DEBUG")
        return httpx.Client(follow_redirects=True, http2=True, verify=True)
    except Exception as e:
        logger.log_text(f"Failed to get HTTP client: {str(e)}", severity="ERROR")
        return None
    
def fetch_calendar_data(client: httpx.Client, url: str, logger: gcp_logging.Logger) -> str:
    try:
        response = client.get(url)
        response.raise_for_status()  # Ensure we got a successful response
        return response.text
    except httpx.HTTPError as e:
        logger.log_text(f"Failed to fetch calendar data: {str(e)}", severity="ERROR")
        raise

def parse_calendar_html(html: str, logger: gcp_logging.Logger) -> pd.DataFrame:
    soup = BeautifulSoup(html, 'html.parser')
    calendar = soup.select("ul.calendario")
    if not calendar:
        logger.log_text("No calendar data found in HTML", severity="WARNING")
        return pd.DataFrame()

    title_elements = calendar[0].select("div.views-field.views-field-title")
    divulga_data = calendar[0].select("div.views-field.views-field-field-divulgacao-data")
    divulga_hora = calendar[0].select("div.views-field.views-field-field-divulgacao-horario")

    data = []
    for idx, (title, data_value, hora_value) in enumerate(zip(title_elements, divulga_data, divulga_hora)):
        try:
            data.append({
                'title': title.get_text(),
                'divulgacao': pd.to_datetime(
                    data_value.get_text(),
                    dayfirst=True
                ),
                'hora': hora_value.get_text()
            })
        except ValueError as e:
            logger.log_text(f"Error parsing calendar data at index {idx}: {str(e)}", severity="WARNING")

    df = pd.DataFrame(data)
    
    if df.empty:
        logger.log_text("DataFrame is empty after parsing", severity="WARNING")
        return df
    
    pattern_ref = r'([A-Za-z]+/\d{4})'
    df['reference'] = df['title'].str.extract(pattern_ref)

    try:
        with open('src/fgv_ibre/month_map.json', 'r') as f:
            month_mapping = json.load(f)
    except FileNotFoundError:
        logger.log_text("File 'month_map.json' not found", severity="ERROR")
        return pd.DataFrame()

    df['reference'] = df['reference'].replace(month_mapping, regex=True)
    df['reference'] = pd.to_datetime(df['reference'], format='%B/%Y', errors='coerce')
    df['title'] = df['title'].str.replace(pattern_ref, '', regex=True).str.strip(' -')
    
    df.dropna(inplace=True)

    try:
        with open('src/fgv_ibre/cat_fgv.json', 'r') as f:
            cat_fgv_df = pd.read_json(f)
    except FileNotFoundError:
        logger.log_text("File 'cat_fgv.json' not found", severity="ERROR")
        return pd.DataFrame()

    df = pd.merge(df, cat_fgv_df, left_on='title', right_on='indice', how='right')
    df.set_index('divulgacao', drop=True, inplace=True)
    df['hora'] = df['hora']
    df = df.drop('indice', axis=1)
    df = df.dropna().sort_index(ascending=True)
    # Correct the parsing of 'codes' and 'meta'
    df['meta'] = df['meta'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    df['codes'] = df['codes'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    today = datetime.today().date()

    try:
        df = df.loc[(df.index == f'{today}')]
        if df.empty:
            logger.log_text("No indicators scheduled for release today", severity="INFO")
        else:
            logger.log_text(f"{len(df)} indicators scheduled for release today", severity="INFO")
        return df
    except KeyError:
        logger.log_text("KeyError: No data for today", severity="WARNING")
        return pd.DataFrame()  # Empty DataFrame if no data for today

def run_crawler(logger:gcp_logging.Logger, **kwargs) -> pd.DataFrame:
    base_url = "https://portalibre.fgv.br/"
    calendar_url = f"{base_url}calendario-de-divulgacao"

    client = _get_client(logger)
    if client is None:
        return None
    
    try:
        # Now use the same session to fetch the calendar data
        html = fetch_calendar_data(client, calendar_url, logger)
        df = parse_calendar_html(html, logger)
    
        if isinstance(df, pd.DataFrame) and not df.empty:
            logger.log_text(f"{len(df)} indicators release predicted for today", severity="INFO")
            return df
        elif isinstance(df, pd.Series) and not df.empty:
            logger.log_text(f"{len(df)} indicators release predicted for today", severity="INFO")
            return df.to_frame().T
        else:
            logger.log_text("No data returned from FGV scheduler", severity="INFO")
            return None
    except Exception as e:
        logger.log_text(f"An error occurred in run_crawler: {str(e)}", severity="ERROR")
        return None
