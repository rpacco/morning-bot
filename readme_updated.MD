# Indicadores Brasil Bot 🇧🇷📊

## Visão Geral

O **Indicadores Brasil Bot** é um projeto automatizado projetado para coletar, processar, visualizar e divulgar dados econômicos e sociais chave do Brasil. Ele busca em várias fontes de dados oficiais e confiáveis, gera visualizações informativas e compartilha essas percepções por meio de tweets automatizados, fornecendo atualizações oportunas sobre o cenário brasileiro.

## Fontes de Dados

O bot atualmente coleta dados das seguintes fontes:

* **ANFAVEA (Associação Nacional dos Fabricantes de Veículos Automotores):** Dados sobre a indústria automobilística, incluindo produção, exportação e licenciamento.
* **BCB (Banco Central do Brasil):** Estatísticas fiscais (resultado primário, juros), atividade econômica (IBC-Br), balanço de pagamentos, investimentos diretos no país, estatísticas monetárias e de crédito (M2, SFN) e taxas de juros.
* **FGV-IBRE (Fundação Getulio Vargas - Instituto Brasileiro de Economia):** Índices de confiança (empresarial, consumidor, construção, indústria, comércio, serviços), indicador de incerteza econômica, indicador antecedente de emprego, índice de variação de aluguéis residenciais (IVAR), índices de preços (IGP-DI, IGP-10, IGP-M) e Monitor do PIB.
* **IBGE (Instituto Brasileiro de Geografia e Estatística):** Índices de inflação (IPCA, IPCA-15), índice de preços ao produtor, pesquisa mensal de comércio, pesquisa mensal de serviços, pesquisa industrial mensal e Produto Interno Bruto (PIB).
* **ABICOM (Associação Brasileira dos Importadores de Combustíveis):** Dados de Paridade de Preços de Importação (PPI) para diesel e gasolina.
* **SSP-SP (Secretaria de Segurança Pública de São Paulo):** Estatísticas de criminalidade, especificamente dados de roubos para o estado e capital de São Paulo.

## Funcionalidades Principais

* **Coleta de Dados Multi-fonte:** Extrai dados de diversas APIs e sites brasileiros.
* **Agendamento Automatizado:** Verifica calendários de divulgação e executa crawlers nos dias corretos.
* **Processamento de Dados:** Limpa, transforma e analisa os dados brutos usando Pandas.
* **Geração de Visualizações:** Cria gráficos e visualizações informativas usando Matplotlib e Seaborn.
* **Criação de Tweets:** Gera textos de tweets dinâmicos resumindo as últimas descobertas.
* **Publicação Automatizada:** Posta os tweets gerados com suas visualizações correspondentes usando Tweepy.
* **Logging e Monitoramento:** Mantém registros das operações e lida com erros de forma robusta.
* **Integração com a Nuvem:** Utiliza serviços de nuvem para armazenamento de logs e dados (inferido a partir de `utils/bucket_conn.py` e `utils/bq_conn.py`).

## Estrutura do Projeto

O projeto é organizado em módulos, cada um responsável por uma fonte de dados específica:
```src/
├── anfavea/         # Módulo para ANFAVEA
│   ├── anfa.py
│   ├── anfa_calendar.py
│   ├── gen_viz.py
│   └── tweet.py
├── bcb/             # Módulo para Banco Central do Brasil
│   ├── bcb.py
│   ├── bcb_sched.py
│   ├── cat_bcb.json
│   ├── gen_viz.py
│   ├── month_map.json
│   └── tweet.py
├── fgv_ibre/        # Módulo para FGV-IBRE
│   ├── cat_fgv.json
│   ├── client_login.py
│   ├── fgv_ibre.py
│   ├── fgv_sched.py
│   ├── gen_viz.py
│   ├── month_map.json
│   └── tweet.py
├── ibge/            # Módulo para IBGE
│   ├── cat_ibge.csv
│   ├── gen_viz.py
│   ├── ibge.py
│   ├── ibge_sched.py
│   └── tweet.py
├── abicom/          # Módulo para ABICOM
│   ├── gen_viz.py
│   ├── ppi.py
│   └── tweet.py
├── ssp/             # Módulo para SSP-SP
│   ├── gen_viz.py
│   ├── ssp.py
│   └── tweet.py
├── utils/           # Módulos utilitários (conexões, etc.)
│   ├── bucket_conn.py
│   └── bq_conn.py
├── run_anfavea.py   # Script principal para ANFAVEA
├── run_bcb.py       # Script principal para BCB
├── run_fgv.py       # Script principal para FGV
├── run_ibge.py      # Script principal para IBGE
├── run_ppi.py       # Script principal para ABICOM
└── run_ssp.py       # Script principal para SSP
```

Cada `run_*.py` atua como o orquestrador para sua fonte de dados respectiva, lidando com a verificação de agendamento, busca de dados, geração de visualizações e tweeting. Os subdiretórios contêm a lógica específica para interagir com cada fonte, processar seus dados e criar os outputs.

## Tecnologias Utilizadas

* **Python:** Linguagem principal do projeto.
* **Pandas:** Para manipulação e análise de dados.
* **Matplotlib & Seaborn:** Para criação de gráficos e visualizações.
* **Tweepy:** Para interagir com a API do Twitter.
* **httpx & requests:** Para realizar requisições HTTP.
* **BeautifulSoup:** Para fazer parsing de HTML.
* **Google Cloud Platform (GCP):** Para logging e possivelmente armazenamento e execução.

## Configuração e Uso

1.  **Clonar o Repositório:**
    ```bash
    git clone <url-do-repositorio>
    cd <nome-do-repositorio>
    ```
2.  **Instalar Dependências:** (Assumindo um arquivo `requirements.txt`)
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configurar Variáveis de Ambiente:** Crie um arquivo `.env` ou configure as variáveis de ambiente necessárias, incluindo:
    * Credenciais da API do Twitter (`CONSUMER_KEY`, `CONSUMER_SECRET`, `ACCESS_TOKEN`, `ACCESS_SECRET`, `BEARER_TOKEN`).
    * Credenciais do Portal FGV (`FGV_USER`, `FGV_PASSWORD`).
    * Configurações do Google Cloud (`PROJECT_ID`, `DATASET_ID`, `TABLE_ID`).
    * Credenciais do Google Cloud (geralmente via `GOOGLE_APPLICATION_CREDENTIALS`).
4.  **Executar os Módulos:** Execute os scripts `run_*.py` individualmente ou configure um agendador (como `cron` ou um serviço de nuvem) para executá-los conforme necessário.

## Contribuição

Contribuições são bem-vindas! Se você deseja adicionar novas fontes de dados, melhorar as visualizações, otimizar o código ou corrigir bugs, sinta-se à vontade para abrir uma *issue* ou enviar um *pull request*.

---