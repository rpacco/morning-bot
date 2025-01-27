import pandas as pd
import requests
import seaborn as sns
import matplotlib.pyplot as plt
import json
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, FixedLocator
from datetime import datetime
import matplotlib.lines as mlines
import numpy as np


def get_data(ano: str, tipo: str, grupo: str):
    dict_months = {
        'janeiro': 1,
        'fevereiro': 2,
        'marco': 3,
        'abril': 4,
        'maio': 5,
        'junho': 6,
        'julho': 7,
        'agosto': 8,
        'setembro': 9,
        'outubro': 10,
        'novembro': 11,
        'dezembro': 12
    }
    url_base = f'https://www.ssp.sp.gov.br/v1/OcorrenciasMensais/RecuperaDadosMensaisAgrupados?ano={ano}&grupoDelito=6&tipoGrupo={tipo}&idGrupo={grupo}'
    response = requests.get(url_base)
    json_raw = json.loads(response.content)['data'][0]['listaDados']
    df_raw = pd.DataFrame(json_raw)
    df = df_raw[['janeiro',
        'fevereiro', 'marco', 'abril', 'maio', 'junho', 'julho', 'agosto',
        'setembro', 'outubro', 'novembro', 'dezembro']]
    delito_df = df_raw['delito'].apply(pd.Series)['delito']
    df = df.T
    df.columns = delito_df
    # Map month names to numbers and convert to string, append the year, and convert all to datetime
    df['date'] = df.index.map(dict_months).astype(str) + '-' + ano
    df['date'] = pd.to_datetime(df['date'], format="%m-%Y")
    df.set_index('date', drop=True, inplace=True)
    # Drop rows where all values are 0
    df = df.loc[~(df == 0).all(axis=1), ['TOTAL DE ROUBO - OUTROS (1)']]

    return df


def wrangle_data():
    estado_df = pd.concat([get_data(str(year), 'ESTADO', '0') for year in range(2022, int(datetime.today().date().year))], axis=0)
    capital_df = pd.concat([get_data(str(year), 'REGIÃO', '1') for year in range(2022, int(datetime.today().date().year))], axis=0)

    merged_df = estado_df.merge(capital_df, on='date', suffixes=['_estado', '_capital'])
    merged_df.columns = [col.split('_')[-1] for col in merged_df.columns]
    merged_df['data'] = merged_df.index.strftime('%b/%y')
    merged_df = merged_df.iloc[-25:,]

    return merged_df