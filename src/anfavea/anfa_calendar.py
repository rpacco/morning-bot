import httpx
from bs4 import BeautifulSoup
import re
import pandas as pd


# Function to filter valid dates
def find_dates(elements):
    pattern = r'\b\d{2}/\d{2}/\d{4}\b'
    valid_dates = []
    for element in elements:
        # Extract text from the element
        text = element.get_text()
        # Search for the pattern in the text
        matches = re.findall(pattern, text)
        if matches:
            valid_dates.extend(matches)
    return valid_dates

def check_release_date():
    url = 'https://anfavea.com.br/site/'

    response = httpx.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    h4_list = soup.find_all('h4')
    release_date_raw = find_dates(h4_list)
    release_date = pd.to_datetime(release_date_raw[0], format='%d/%m/%Y').date()

    return release_date
