import httpx
from datetime import datetime, date, timedelta
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Dict
import re
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, RetryError

class PpiCrawler:
    def __init__(self, start_date: datetime.date):
        self.name = "ppi_crawler"
        self.allowed_domains = ["abicom.com.br"]
        self.base_url = "https://abicom.com.br"
        self.today = datetime.today().date()
        self.start_date = start_date

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(5), retry=retry_if_exception_type(httpx.HTTPError))
    def _safe_request(self, client: httpx.Client, url: str):
        try:
            response = client.get(url, timeout=10)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"Request failed for {url}: {e}")
            return None

    def check_date(self, client: httpx.Client) -> bool:
        response = self._safe_request(client, f"{self.base_url}/categoria/ppi/")
        if response is None:
            return False

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Parse the response to get the last date from the page content
        last_date_text = soup.find('h5', class_="card-title").get_text(strip=True).split(' - ')[-1]
        try:
            last_date = pd.to_datetime(last_date_text, dayfirst=True).date()
            return last_date == self.today
        except ValueError:
            print(f"Failed to parse date {last_date_text}")
            return False
    
    def _process_content(self, content_raw: List[str]) -> Dict[str, float]:
        curated_def_pct = [s for s in content_raw if s.strip().startswith('Defasagem média de')]
        percentage_pattern = r'([-+]?\d+\%)'
        percentage_matches = []

        for s in curated_def_pct:
            matches = re.findall(percentage_pattern, s)
            percentage_matches.extend(matches)
        
        if percentage_matches:
            diesel_pct = float(percentage_matches[0].replace('%', ''))
            gasolina_pct = float(percentage_matches[-1].replace('%', ''))
        else:
            diesel_pct = None
            gasolina_pct = None

        joined_content = ''.join(content_raw)
        curated_def_brl = re.compile(r'média de[:]?[\n]?[ ]?([+-–]?R\$[0-9,]+)', re.DOTALL)
        brl_pattern_list = curated_def_brl.findall(joined_content)
        
        diesel_brl = float(brl_pattern_list[0].strip().replace('R$', '').replace(',', '.').replace('–', '-').replace('L', ''))
        gasolina_brl = float(brl_pattern_list[1].strip().replace('R$', '').replace(',', '.').replace('–', '-').replace('L', ''))

        return {
            'diesel_pct': diesel_pct,
            'diesel_brl': diesel_brl,
            'gasolina_pct': gasolina_pct,
            'gasolina_brl': gasolina_brl
        }

    def fetch_content(self, client: httpx.Client, date: str) -> Dict[str, float]:
        url = f"{self.base_url}/ppi/ppi-{date}/"
        response = self._safe_request(client, url)
        date_norm = pd.to_datetime(date, dayfirst=True).date().strftime('%Y-%m-%d')
        if response is None:
            return {'date': date_norm, 'diesel_pct': None, 'diesel_brl': None, 'gasolina_pct': None, 'gasolina_brl': None}

        soup = BeautifulSoup(response.text, 'html.parser')
    
        content_div = soup.select_one('div.page-content.blog-content')
        content_raw = [elem.get_text(strip=True) for elem in content_div.descendants if elem.name is None]

        processed_content = self._process_content(content_raw)
        
        # Unnest content keys and combine with date
        return {**{'date': date_norm}, **processed_content}

    def run(self):
        with httpx.Client() as client:
            if self.check_date(client):
                print("Latest date matches today's date, continuing the script.")

                date_range_raw = pd.date_range(start=self.start_date, end=self.today, freq='B')
                date_range = [date.strftime('%d-%m-%Y') for date in date_range_raw]

                results = []
                for date in date_range:
                    try:
                        result = self.fetch_content(client, date)
                        results.append(result)
                    except Exception as e:
                        print(f"Error processing data for date {date}: {e}")

                return results  # Return collected results

            else:
                print("Latest date does not match today's date, stopping the crawler.")
                return None  # Return an empty list if the crawl was stopped
