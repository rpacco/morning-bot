import httpx
from bs4 import BeautifulSoup
import pandas as pd
import io

def get_xls_link():
    url = 'https://anfavea.com.br/site/edicoes-em-excel/'
    response = httpx.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    series_hist_elem = soup.find('div', class_='et_pb_tab_content')
    link_elem = series_hist_elem.find_all('a')
    links = {
        link.get_text(strip=True): link.get('href') for link in link_elem
    }
    target_string = '(automóveis, comerciais leves, caminhões, ônibus, total)'
    target_url = next((url for key, url in links.items() if target_string in key), None)
    

    return target_url

def read_excel(url):
    response = httpx.get(url)
    with io.BytesIO(response.content) as file:
        df = pd.read_excel(
            file, 
            header=4,  # Use row 5 (0-indexed) as the header
            index_col=0,  # Use column A as the index
            usecols='A:F',  # Select columns B to F
            engine='openpyxl',  # Use openpyxl engine for .xlsm files
            parse_dates=True
        )
    return df.iloc[-24:,]
