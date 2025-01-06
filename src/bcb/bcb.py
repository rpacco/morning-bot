from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, RetryError
import pandas as pd
from src.bcb.bcb_sched import bcb_calendar
from datetime import datetime
import httpx
import json
import time


@retry(stop=stop_after_attempt(3), wait=wait_fixed(5), retry=retry_if_exception_type(httpx.HTTPError))
def call_api(url, headers):
    try:
        response = httpx.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an exception for non-2xx status codes
        return response
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

def get_bc_serie(series: list, name: str, colunas: list, reference: datetime.date, raw: bool = False, multiplicador: int = 1):
    data = []
    for serie in series:
        api_url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie}/dados?formato=json"
        headers = {
            'Accept': 'application/json, text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.5',
            'Host': 'api.bcb.gov.br',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0'
        }
        
        try:
            response = call_api(api_url, headers)
            json_raw = json.loads(response.text)
            df = pd.DataFrame(json_raw)
            df['data'] = pd.to_datetime(df['data'], dayfirst=True)
            data.append(df)
            time.sleep(5)
        except RetryError as e:
            print(f"Failed to retrieve data for series {serie} after multiple retries. Error: {e}")
            return None
        except Exception as e:
            print(f"No data for series {serie}. Error: {e}")
            return None
        
    if data:
        df_merged = data[0]
        for df in data[1:]:
            df_merged = pd.merge(df_merged, df, on='data')
        
        df_merged.set_index('data', drop=True, inplace=True)
        df_merged.columns = colunas
        df_merged['MoM'] = pd.to_numeric(df_merged['MoM'], errors='coerce')
        df_merged['YoY'] = pd.to_numeric(df_merged['YoY'], errors='coerce')
        df_merged = df_merged * multiplicador
        df_merged.name = name
        
    
        if raw:
            df_merged['MoM'] = df_merged['MoM'].pct_change(1) * 100
            # df_merged['YoY'] = df_merged['YoY'].pct_change(12) * 100
            df_merged['YoY'] = ((df_merged['YoY'].rolling(12).sum() / df_merged['YoY'].shift(12).rolling(12).sum()) - 1)*100

        if df_merged.index[-1].date() == reference.date():
            return df_merged
        else:
            print('Dados não atualizados na fonte')
            return None
    else:
        return None
