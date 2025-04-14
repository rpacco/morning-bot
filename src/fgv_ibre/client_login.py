import httpx
import time
import re
from urllib.parse import unquote
from google.cloud import logging as gcp_logging

class FGVPortalClient:
    BASE_URL = "https://autenticacao-ibre.fgv.br/ProdutosDigitais"
    API_VERSION = "c5XRe9RikgJxYypxDkypFw"
    DEFAULT_HEADERS = {
        "Accept": "application/json",
        "OutSystems-client-env": "browser"
    }

    def __init__(self, max_retries: int = 2, gcp_logging_client: gcp_logging.Client = None):
        self.client = httpx.Client(follow_redirects=True, timeout=10.0)
        self.csrf_token: str | None = None
        self.module_version: str | None = None
        self.current_url: str | None = None
        self.max_retries = max_retries
        self.gcp_logger = gcp_logging_client or gcp_logging.Client()

    def login(self, username: str, password: str) -> httpx.Client | bool:
        """Handle the complete login flow to FGV Portal with retry mechanism"""
        try:
            self._initialize_session()
            self._fetch_module_version()
            self._fetch_module_info()
            self._refresh_csrf_token()

            for attempt in range(self.max_retries):
                result = self._attempt_login(username, password)
                if isinstance(result, httpx.Client):
                    return self.client
                elif result == "retry":
                    self.gcp_logger.log_text(f"Retrying login with new CSRF token (attempt {attempt+1}/{self.max_retries})", severity="WARNING")
                    self._refresh_csrf_token()
                else:
                    return False

            self.gcp_logger.log_text(f"Failed to login after {self.max_retries} attempts", severity="ERROR")
            return False
        except httpx.NetworkError as e:
            self.gcp_logger.log_text(f"Network error during login: {e}", severity="ERROR")
            return False
        except Exception as e:
            self.gcp_logger.log_text(f"Unexpected error: {e}", severity="ERROR")
            return False

    def _initialize_session(self):
        """Visita a página inicial do portal"""
        self.gcp_logger.log_text("Visiting initial portal page...", severity="INFO")
        response = self.client.get("https://portalibre.fgv.br/")
        self.current_url = str(response.url)

    def _fetch_module_version(self):
        """Obtém a versão do módulo necessária para autenticação"""
        timestamp = int(time.time() * 1000)
        url = f"{self.BASE_URL}/moduleservices/moduleversioninfo?{timestamp}"
        headers = self.DEFAULT_HEADERS | {"Referer": self.BASE_URL + "/"}

        self.gcp_logger.log_text("Getting module version info...", severity="INFO")
        response = self._make_request("GET", url, headers=headers)
        version_info = response.json()
        self.module_version = version_info.get('versionToken')
        self.gcp_logger.log_text(f"Module version: {self.module_version}", severity="INFO")

    def _fetch_module_info(self):
        """Busca informações do módulo com o token de versão"""
        url = f"{self.BASE_URL}/moduleservices/moduleinfo?{self.module_version}"
        headers = self.DEFAULT_HEADERS | {"Referer": self.BASE_URL + "/"}
        
        self.gcp_logger.log_text("Getting module info...", severity="INFO")
        self._make_request("GET", url, headers=headers)

    def _refresh_csrf_token(self):
        """Atualiza o token CSRF a partir dos cookies"""
        self.csrf_token = self._extract_csrf_token_from_cookies()
        if self.csrf_token:
            self.gcp_logger.log_text(f"CSRF token refreshed: {self.csrf_token}", severity="DEBUG")
        else:
            self.gcp_logger.log_text("No CSRF token found in cookies.", severity="WARNING")

    def _attempt_login(self, username: str, password: str):
        """Tenta realizar o login uma vez"""
        url = f"{self.BASE_URL}/screenservices/ProdutosDigitais/Blocks/BL01_Login/DataActionGetDados"
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Origin": "https://autenticacao-ibre.fgv.br",
            "Referer": self.BASE_URL + "/"
        } | self.DEFAULT_HEADERS
        if self.csrf_token:
            headers["X-CSRFToken"] = self.csrf_token

        payload = self._build_login_payload(username, password)

        self.gcp_logger.log_text("Sending login request...", severity="INFO")
        response = self._make_request("POST", url, headers=headers, json=payload)
        
        # Tenta atualizar o CSRF token da resposta
        new_csrf = self._extract_csrf_token_from_header(response.headers.get('set-cookie', ''))
        if new_csrf:
            self.csrf_token = new_csrf
            self.gcp_logger.log_text(f"Updated CSRF token from response: {self.csrf_token}", severity="DEBUG")

        return self._handle_login_response(response)

    def _build_login_payload(self, username: str, password: str) -> dict:
        """Monta o payload para a requisição de login"""
        return {
            "versionInfo": {"moduleVersion": self.module_version, "apiVersion": self.API_VERSION},
            "viewName": "MainFlow.Login",
            "screenData": {
                "variables": {
                    "DS_Login": username,
                    "DS_Password": password,
                    "FLG_ExibirSenha": False,
                    "MSG_Erro": "",
                    "Prompt_Login": "",
                    "Prompt_Senha": "",
                    "FLG_PopupAtivarConta": False,
                    "Loading": True,
                    "FLG_AtivacaoCadastro": False,
                    "MSG_AtivacaoCadastro": "",
                    "FLG_ativarConta": False,
                    "_fLG_ativarContaInDataFetchStatus": 1,
                    "token": "",
                    "_tokenInDataFetchStatus": 1,
                    "Email": "",
                    "_emailInDataFetchStatus": 1
                }
            },
            "clientVariables": {
                "LastURL": "",
                "RL_Produtos": "",
                "Username": "",
                "NM_Usuario": ""
            }
        }

    def _handle_login_response(self, response: httpx.Response):
        """Processa a resposta do login"""
        if response.status_code == 200:
            data = response.json()
            self.gcp_logger.log_text("Login request successful", severity="INFO")
            if data['data']['FLG_Sucesso']:
                self.gcp_logger.log_text(f"Login success: {data['data']['DS_Msg']}", severity="INFO")
                free_url = data['data'].get('URL_Gratuito')
                self.gcp_logger.log_text(f"Redirecting to free URL: {free_url}", severity="INFO")
                try:
                    # Redireciona para a URL gratuita e atualiza o cliente
                    free_url_response = self.client.get(free_url)  # Usa self.client diretamente
                    if 200 <= free_url_response.status_code < 300:
                        self.gcp_logger.log_text("Successfully accessed free URL", severity="INFO")
                        self.current_url = free_url
                        self.gcp_logger.log_text("Returning client...", severity="INFO")
                        return self.client
                    else:
                        self.gcp_logger.log_text(f"Unexpected status code accessing free URL: {free_url_response.status_code}", severity="WARNING")
                except Exception as e:
                    self.gcp_logger.log_text(f"Fatal error after redirect: {e}", severity="ERROR")
                except httpx.RequestError as e:
                    self.gcp_logger.log_text(f"Request error accessing free URL: {e}", severity="ERROR")
            else:
                self.gcp_logger.log_text(f"Login failed: {data['data']['DS_Msg']}", severity="ERROR")
                return False
        else:
            self.gcp_logger.log_text(f"Login failed with status code: {response.status_code}", severity="ERROR")
            if response.status_code in [401, 403]:
                return "retry"
            return False

    def _make_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Wrapper genérico para requisições HTTP com tratamento básico de erros"""
        try:
            response = self.client.request(method, url, **kwargs)
            response.raise_for_status()  # Lança exceção para 4xx/5xx
            self.current_url = str(response.url)
            return response
        except httpx.HTTPStatusError as e:
            self.gcp_logger.log_text(f"HTTP error {e.response.status_code} for {url}", severity="ERROR")
            return response
        except httpx.RequestError as e:
            self.gcp_logger.log_text(f"Request error for {url}: {e}", severity="ERROR")
            raise

    def _extract_csrf_token_from_cookies(self) -> str | None:
        """Extrai CSRF token dos cookies do cliente"""
        for cookie in self.client.cookies.jar:
            if cookie.name == 'nr2Users':
                return self._parse_csrf_from_value(cookie.value)
        return None

    def _extract_csrf_token_from_header(self, set_cookie: str) -> str | None:
        """Extrai CSRF token do header Set-Cookie"""
        if set_cookie and 'nr2Users=' in set_cookie:
            match = re.search(r'nr2Users=crf%3d([^;]+)', set_cookie)
            if match:
                return self._parse_csrf_from_value(unquote(match.group(1)))
        return None

    @staticmethod
    def _parse_csrf_from_value(value: str) -> str | None:
        """Faz o parse do valor do cookie nr2Users para extrair o token CSRF"""
        if 'crf%3d' in value:
            token_with_extra = unquote(value.split('crf%3d')[1])
            token = token_with_extra.split(';')[0]
            token = token.replace('%2b', '+').replace('%2f', '/').replace('%3d', '=')
            return token
        return None

    def get_current_url(self) -> str | None:
        """Retorna a URL atual"""
        return self.current_url

    def close(self):
        """Fecha a sessão do cliente"""
        if self.client:
            self.client.close()
