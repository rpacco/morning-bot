import httpx
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

def fetch_calendar_data(url: str) -> str:
    with httpx.Client(follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()  # Ensure we got a successful response
        return response.text

def parse_calendar_html(html: str) -> pd.DataFrame:
    soup = BeautifulSoup(html, 'html.parser')
    calendar = soup.select("ul.agenda--lista")
    title_elements = calendar[0].select("div.agenda--lista__evento")
    divulga_data = calendar[0].select("div.agenda--lista__data")
    ref_data = calendar[0].select("p.metadados.metadados--agenda")
    data = []
    for title, data_value, ref_value in zip(title_elements, divulga_data, ref_data):
        data.append({
            'title': title.get_text(strip=True),
            'divulgacao': pd.to_datetime(
                data_value.get_text(strip=True),
                dayfirst=True
            ),
            'referencia': ref_value.get_text(strip=True)
        })

    df = pd.DataFrame(data)
    df['title'] = df['title'].str.replace('Período de referência.*', '', regex=True)
    df['referencia'] = df['referencia'].str.extract(r': (\d{1,2}/\d{4})')
    df['referencia'] = pd.to_datetime(df['referencia'], format='%m/%Y')

    with open('src/ibge/cat_ibge.csv', 'r') as f:
        cat_ibge_df = pd.read_csv(f, delimiter=',', dtype=str)

    df = pd.merge(df, cat_ibge_df, left_on='title', right_on='indicator', how='left')
    df['divulgacao'] = pd.to_datetime(df['divulgacao'])
    df.set_index('divulgacao', drop=True, inplace=True)
    df = df.drop('indicator', axis=1)
    df = df.dropna().sort_index(ascending=True)

    today = datetime.today().date()

    try:
        df = df.loc[f'{today}']
        return df
    except KeyError:
        return pd.DataFrame()  # Empty DataFrame if no data for today

def run_crawler(logger=None, **kwargs) -> pd.DataFrame:
    url = "https://www.ibge.gov.br/calendario-de-divulgacoes-novoportal.html"
    html = fetch_calendar_data(url)
    df = parse_calendar_html(html)
    
    if isinstance(df, pd.DataFrame) and not df.empty:
        if logger:
            logger.log_text(f"{len(df)} indicators release predicted for today", severity="INFO")
        return df
    elif isinstance(df, pd.Series) and not df.empty:
        if logger:
            logger.log_text(f"{len(df)} indicators release predicted for today", severity="INFO")
        return df.to_frame().T
    else:
        if logger:
            logger.log_text("No data returned from IBGE scheduler", severity="WARNING")
        return None