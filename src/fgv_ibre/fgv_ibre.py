from .client_login import FGVPortalClient
import httpx
import pandas as pd
from bs4 import BeautifulSoup
from google.cloud import logging as gcp_logging
import io

class FGVSpider:
    def __init__(self, client=None, serie=None, columns=None, logger=None, ref_date=None):
        """
        Modificação do construtor para aceitar o client já autenticado como parâmetro.
        """
        self.client = client  # Agora recebemos o client já autenticado
        self.base_url = "https://extra-ibre.fgv.br/IBRE/sitefgvdados/default.aspx"
        self.serie = serie
        self.result_df = pd.DataFrame()
        self.columns = columns
        self.ref_date = ref_date
        if logger is None:
            # Set up Google Cloud Logger
            client = gcp_logging.Client()
            self.logger = client.logger('fgv_spider')
        else:
            self.logger = logger
        self.logger.log_text(f"Spider initialized with serie: {self.serie} and columns: {self.columns}", severity="INFO")

    def _get_initial_page(self):
        try:
            self.logger.log_text("Getting initial page", severity="DEBUG")
            # Aqui estamos fazendo o "refresh" da página utilizando a URL já logada
            response = self.client.get(self.base_url)  # Usando a base_url que foi configurada
            self.logger.log_text(f"Initial page response status code: {response.status_code}", severity="DEBUG")
            return response
        except Exception as e:
            self.logger.log_text(f"Failed to get initial page: {str(e)}", severity="ERROR")
            return None

    def _parse_initial_page(self, response):
        try:
            self.logger.log_text("Parsing initial page", severity="DEBUG")
            soup = BeautifulSoup(response.text, 'html.parser')
            form_data = self._get_initial_form_data(soup)
            form_data["ctl00$txtBuscarSeries"] = ','.join(self.serie)
            for i in range(len(self.serie)):
                form_data[f"ctl00$cphConsulta$dlsSerie$ctl0{i}$chkSerieEscolhida"] = "on"
            self.logger.log_text("Posting form data to initial page", severity="DEBUG")
            return self._post_form(response.url, form_data)
        except Exception as e:
            self.logger.log_text(f"Failed to parse initial page: {str(e)}", severity="ERROR")
            return None

    def _parse_step2_page(self, response):
        try:
            self.logger.log_text("Parsing step 2 page", severity="DEBUG")
            soup = BeautifulSoup(response.text, 'html.parser')
            form_data = self._get_step2_form_data(soup)
            form_data["ctl00$txtBuscarSeries"] = ','.join(self.serie)
            for i in range(len(self.serie)):
                form_data[f"ctl00$cphConsulta$dlsSerie$ctl0{i}$chkSerieEscolhida"] = "on"
                form_data[f"ctl00$dlsSerie$ctl0{i}$chkSerieEscolhida"] = "on"
            self.logger.log_text("Posting form data to step 2 page", severity="DEBUG")
            return self._post_form(response.url, form_data)
        except Exception as e:
            self.logger.log_text(f"Failed to parse step 2 page: {str(e)}", severity="ERROR")
            return None

    def _parse_step3_page(self, response):
        try:
            self.logger.log_text("Parsing step 3 page", severity="DEBUG")
            soup = BeautifulSoup(response.text, 'html.parser')
            form_data = self._get_step3_form_data(soup)
            form_data["ctl00$txtBuscarSeries"] = ','.join(self.serie)
            for i in range(len(self.serie)):
                form_data[f"ctl00$dlsSerie$ctl0{i}$chkSerieEscolhida"] = "on"
                form_data[f"ctl00$cphConsulta$dlsSerie$ctl0{i}$chkSerieEscolhida"] = "on"
            form_data["ctl00$cphConsulta$butVisualizarResultado"] = "Visualizar e salvar"
            form_data["ctl00$txtBuscarSeries"] = ""
            self.logger.log_text("Posting form data to step 3 page", severity="DEBUG")
            return self._post_form(response.url, form_data)
        except Exception as e:
            self.logger.log_text(f"Failed to parse step 3 page: {str(e)}", severity="ERROR")
            return None

    def _parse_results(self, response):
        try:
            self.logger.log_text("Parsing results page", severity="DEBUG")
            soup = BeautifulSoup(response.text, 'html.parser')
            iframe = soup.find('iframe', id='cphConsulta_ifrVisualizaConsulta')
            if iframe:
                iframe_src = iframe.get('src')
                self.logger.log_text("Getting iframe content", severity="DEBUG")
                return self.client.get(f"https://extra-ibre.fgv.br{iframe_src}")
        except Exception as e:
            self.logger.log_text(f"Failed to parse results page: {str(e)}", severity="ERROR")
            return None

    def _parse_iframe_content(self, response):
        try:
            self.logger.log_text("Parsing iframe content", severity="DEBUG")
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', id='xgdvConsulta_DXMainTable')
            if table:
                tables = pd.read_html(io.StringIO(str(table)), header=0)
                df = tables[0]
                df = self._clean_df(df)
                self.logger.log_text(f"DataFrame created with {len(df)} rows.", severity="DEBUG")
                return df
        except Exception as e:
            self.logger.log_text(f"Failed to parse iframe content: {str(e)}", severity="ERROR")

    def _clean_df(self, df):
        try:
            self.logger.log_text("Cleaning DataFrame", severity="DEBUG")
            date_format = len(df['Data'].str.split('/', expand=True).columns)
            df['Data'] = pd.to_datetime(
                df['Data'], 
                format='%m/%Y' if date_format == 2 else '%d/%m/%Y', 
                errors='coerce'
            )
            df.set_index('Data', drop=True, inplace=True)
            df.columns = self.columns
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df_date = df.index[-1].date()
            self.logger.log_text(f"Checking data update: DataFrame last date {df_date}, reference date {self.ref_date}", severity="DEBUG")
            if df_date == self.ref_date:
                return df
            else:
                self.logger.log_text(f"Data not updated on source yet", severity="WARNING")
                return None
        except Exception as e:
            self.logger.log_text(f"Failed to clean DataFrame: {str(e)}", severity="ERROR")
            return None

    def _get_initial_form_data(self, soup):
        try:
            self.logger.log_text("Getting initial form data", severity="DEBUG")
            return {
                "__VIEWSTATE": soup.find('input', id="__VIEWSTATE")['value'],
                "__VIEWSTATEGENERATOR": soup.find('input', id="__VIEWSTATEGENERATOR")['value'],
                "__VIEWSTATEENCRYPTED": '',
                "ctl00$smg": "ctl00$updpgeral|ctl00$butBuscarSeries",
                "ctl00$drpFiltro": "C",
                "ctl00$cphConsulta$rblConsultaHierarquia": "COMPARATIVA",
                "ctl00$cphConsulta$cpeLegenda_ClientState": "false",
                "ctl00$cphConsulta$chkEscolhida": "on",
                "ctl00$cphConsulta$gnResultado": "rbtSerieHistorica",
                "ctl00$cphConsulta$txtMes": "__/__/____",
                "ctl00$cphConsulta$mkeMes_ClientState": "",
                "ctl00$cphConsulta$txtPeriodoInicio": "__/__/____",
                "ctl00$cphConsulta$mkePeriodoInicio_ClientState": "",
                "ctl00$cphConsulta$txtPeriodoFim": "__/__/____",
                "ctl00$cphConsulta$mkePeriodoFim_ClientState": "",
                "ctl00$cphConsulta$chkFormatoAmericano": "on",
                "ctl00$txtBAPalavraChave": "",
                "ctl00$rblTipoTexto": "E",
                "ctl00$txtBAColuna": "",
                "ctl00$txtBAIncluida": "",
                "ctl00$txtBAAtualizada": "",
                "ctl00$butBuscarSeries": "OK"
            }
        except Exception as e:
            self.logger.log_text(f"Failed to get initial form data: {str(e)}", severity="ERROR")
            return None

    def _get_step2_form_data(self, soup):
        try:
            self.logger.log_text("Getting step 2 form data", severity="DEBUG")
            return {
                "__VIEWSTATE": soup.find('input', id="__VIEWSTATE")['value'],
                "__VIEWSTATEGENERATOR": soup.find('input', id="__VIEWSTATEGENERATOR")['value'],
                "__VIEWSTATEENCRYPTED": '',
                "ctl00$smg": "ctl00$updpBuscarSeries|ctl00$butBuscarSeriesOK",
                "ctl00$drpFiltro": "C",
                "ctl00$cphConsulta$rblConsultaHierarquia": "COMPARATIVA",
                "ctl00$cphConsulta$cpeLegenda_ClientState": "false",
                "ctl00$cphConsulta$chkEscolhida": "on",
                "ctl00$cphConsulta$gnResultado": "rbtSerieHistorica",
                "ctl00$cphConsulta$txtMes": "__/__/____",
                "ctl00$cphConsulta$mkeMes_ClientState": "",
                "ctl00$cphConsulta$txtPeriodoInicio": "__/__/____",
                "ctl00$cphConsulta$mkePeriodoInicio_ClientState": "",
                "ctl00$cphConsulta$txtPeriodoFim": "__/__/____",
                "ctl00$cphConsulta$mkePeriodoFim_ClientState": "",
                "ctl00$cphConsulta$chkFormatoAmericano": "on",
                "ctl00$txtBAPalavraChave": "",
                "ctl00$rblTipoTexto": "E",
                "ctl00$txtBAColuna": "",
                "ctl00$txtBAIncluida": "",
                "ctl00$txtBAAtualizada": "",
                "ctl00$butBuscarSeriesOK": "OK"
            }
        except Exception as e:
            self.logger.log_text(f"Failed to get step 2 form data: {str(e)}", severity="ERROR")
            return None

    def _get_step3_form_data(self, soup):
        try:
            self.logger.log_text("Getting step 3 form data", severity="DEBUG")
            return {
                "__VIEWSTATE": soup.find('input', id="__VIEWSTATE")['value'],
                "__VIEWSTATEGENERATOR": soup.find('input', id="__VIEWSTATEGENERATOR")['value'],
                "__VIEWSTATEENCRYPTED": '',
                "ctl00$smg": "ctl00$updpAreaConsulta|ctl00$cphConsulta$butVisualizarResultado",
                "ctl00$drpFiltro": "E",
                "ctl00$cphConsulta$rblConsultaHierarquia": "COMPARATIVA",
                "ctl00$cphConsulta$cpeLegenda_ClientState": "false",
                "ctl00$cphConsulta$chkEscolhida": "on",
                "ctl00$cphConsulta$gnResultado": "rbtSerieHistorica",
                "ctl00$cphConsulta$txtMes": "__/__/____",
                "ctl00$cphConsulta$mkeMes_ClientState": "",
                "ctl00$cphConsulta$txtPeriodoInicio": "__/__/____",
                "ctl00$cphConsulta$mkePeriodoInicio_ClientState": "",
                "ctl00$cphConsulta$txtPeriodoFim": "__/__/____",
                "ctl00$cphConsulta$mkePeriodoFim_ClientState": "",
                "ctl00$cphConsulta$chkFormatoAmericano": "on",
                "ctl00$txtBAPalavraChave": "",
                "ctl00$rblTipoTexto": "E",
                "ctl00$txtBAColuna": "",
                "ctl00$txtBAIncluida": "",
                "ctl00$txtBAAtualizada": ""
            }
        except Exception as e:
            self.logger.log_text(f"Failed to get step 3 form data: {str(e)}", severity="ERROR")
            return None

    def _post_form(self, url, form_data):
        try:
            self.logger.log_text("Posting form data", severity="DEBUG")
            response = self.client.post(url, data=form_data)
            self.logger.log_text(f"Form post response status code: {response.status_code}", severity="DEBUG")
            return response
        except Exception as e:
            self.logger.log_text(f"Failed to post form data: {str(e)}", severity="ERROR")
            return None

    def run(self):
        self.logger.log_text("Running spider", severity="INFO")

        response = self._get_initial_page()
        if response is None:
            self.logger.log_text("Failed to get initial page", severity="ERROR")
            return

        response = self._parse_initial_page(response)
        if response is None:
            self.logger.log_text("Failed to parse initial page", severity="ERROR")
            return

        response = self._parse_step2_page(response)
        if response is None:
            self.logger.log_text("Failed to parse step 2 page", severity="ERROR")
            return

        response = self._parse_step3_page(response)
        if response is None:
            self.logger.log_text("Failed to parse step 3 page", severity="ERROR")
            return

        response = self._parse_results(response)
        if response is None:
            self.logger.log_text("Failed to parse results page", severity="ERROR")
            return

        result_df = self._parse_iframe_content(response)
        if result_df is not None:
            self.result_df = result_df
            self.logger.log_text("Spider run completed successfully", severity="INFO")
        else:
            self.logger.log_text("Spider run did not produce results", severity="WARNING")
        
        return self.result_df