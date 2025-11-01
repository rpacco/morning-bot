import pandas as pd
from pandas.tseries.offsets import BDay
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re
import json


def bcb_calendar(arg, logger = None):
    """
    Fetches events data from the Banco Central do Brasil (BCB) website for a predefined list of items.
    Extracts relevant event information from the HTML content, creates a DataFrame, and returns it.
    Returns:
        pd.DataFrame: A DataFrame containing the extracted event data with columns:
                      'evento', 'dataEvento', 'fimEvento', and 'descricao'.
                      'evento': The event type or name.
                      'dataEvento': The start date and time of the event.
                      'fimEvento': The end date and time of the event (if available).
                      'descricao': The description of the event.
    Note:
        This function fetches event data for the current date until December 31st of the current year.
        The 'descricao' column contains HTML content, and the function extracts text from it.
    """
    lista = [
        'Boletim Regional', 'Eventos no Banco Central', 'Estatísticas do Valores a Receber', 'Focus', 
        'Indicadores', 'Informações ao Banco Central', 'Notas para a imprensa', 'Ranking de Reclamações',
        'Relatório de Economia Bancária', 'Relatório de Inflação', 'Reuniões do CMN e COMOC',
        'Reuniões do Comef', 'Reuniões do Copom', 'Reuniões do Coremec', 'Reuniões do GRC',
        'Índice de atividade econômica (IBC-Br)'
    ]
    today = datetime.today()
    dict_arg = {
        'ano': f'{today.year}-01-31',
        'mes': f'{today.year}-{today.month}-01'
    }
    dataframes = []
    # Fetch data for each item in the predefined list
    for item in lista:
        url = f"https://www.bcb.gov.br/api/servico/sitebcb/agendas?lista={item}&inicioAgenda='{dict_arg[arg]}'&fimAgenda='{today.year}-12-31'"
        response = requests.get(url)
        if response.ok:
            data = response.json().get('conteudo')
            if data:
                dataframes.append(pd.DataFrame(data))
    # Concatenate all DataFrames into a single DataFrame
    df = pd.concat(dataframes)
    # Convert 'dataEvento' column to datetime and set it as the DataFrame index
    df['dataEvento'] = pd.to_datetime(df['dataEvento'])
    df.set_index('dataEvento', drop=True, inplace=True)
    # Convert the datetime index to a string in '%Y-%m-%d' format
    df.index = df.index.strftime('%Y-%m-%d')
    df.sort_index(inplace=True)
    with open('src/bcb/month_map.json', 'r') as file:
        month_map = json.load(file)
    # Extract text content from the 'descricao' column containing HTML
    def update_descricao(row):
        html_content = row['descricao']
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            description_raw = soup.get_text(strip=True).lower()
            pattern = r'(?i)(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s+de\s+(\d{4})'
            match = re.search(pattern, description_raw, re.IGNORECASE)
            if match:
                description_raw = match.group(0).split()
                description = ("".join([month_map[x] if x in month_map.keys() else x for x in description_raw])).replace('de','')
                return pd.to_datetime(description, format='%m%Y')
            else:
                return None
        else:
            return None
    df['descricao'] = df.apply(update_descricao, axis=1)

    ref_dates_cambial = df.query('evento == "Estatísticas do setor externo"').index.to_list()
    if ref_dates_cambial:
        dates_cambial = [(pd.to_datetime(date) + BDay(3)) for date in ref_dates_cambial]
        cambial_evento = 'Fluxo Cambial'
        cambial_fim_evento = None
        cambial_local = None
        cambial_dia_inteiro = 'Não'

        cambial_rows = []
        for dataEvento, descricao in zip(dates_cambial, ref_dates_cambial):
            cambial_rows.append({
                'dataEvento': dataEvento.strftime('%Y-%m-%d'),  # Convert to datetime
                'evento': cambial_evento,
                'fimEvento': cambial_fim_evento,
                'descricao': descricao,
                'local': cambial_local,
                'diaInteiro': cambial_dia_inteiro
            })
        cambial_df = pd.DataFrame(cambial_rows)
        cambial_df.set_index('dataEvento', inplace=True)
        df = pd.concat([df, cambial_df])
        df.sort_index(inplace=True)

    try:
        df = df.loc[f'{today.date()}']
        if isinstance(df, pd.DataFrame):
            logger.log_text(f"{len(df)} indicators release predicted for today", severity="INFO")
            return df
        elif isinstance(df, pd.Series):
            logger.log_text(f"{len(df)} indicators release predicted for today", severity="INFO")
            return df.to_frame().T
        else:
            logger.log_text("No data returned from BCB scheduler", severity="INFO")
            return None
    except:
        logger.log_text(f"No data scheduled for {today.date()}", severity="INFO")
        return None
