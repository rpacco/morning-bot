# @EconDataViz: Um Projeto de divulgação e visualização de Dados no X/Twitter

**Descrição**

O perfil criado (@EconDataViz) é um projeto pessoal que visa fornecer dados e gráficos atualizados de dezenas de indicadores econômicos e sociais. O bot é automatizado e publica regularmente no X/Twitter, proporcionando uma visão geral dos principais indicadores econômicos e sociais.

**Funcionamento**

* Coleta de dados de fontes públicas e privadas, incluindo API's e webscrapping de releases oficiais.
* Tratamento e parsing de dados utilizando ferramentas como BeautifulSoup, requests/httpx e pandas.
* Criação de gráficos personalizados para cada indicador monitorado, utilizando matplotlib e seaborn.
* Uso de ferramentas do Google Cloud Platform (GCP), incluindo Scheduler, Cloud Functions e Big Query, dentro da quota free-tier.
* Integração contínua do código através do Github Actions, garantindo o deploy automático das atualizações.

**Tecnologias Utilizadas**

* Python
* BeautifulSoup
* requests/httpx
* pandas
* matplotlib
* seaborn
* Google Cloud Platform (GCP)
* Github Actions

**Repositório**

Este repositório contém o código-fonte do bot. Você pode encontrar os seguintes diretórios e arquivos:

* `src`: contém os scripts de coleta/tratamento/postagem dos indicadores
* `utils`: contém scripts que tratam dos logs/banco de dados.
* `main.py`: script principal que contem a função para deployment no GCP.
* `.github`: contém workflow file para automatização do deployment
* `requirements.txt`: contém os requisitos a serem instalados pela máquina que hospedará a função principal

**Contato**

Se você tiver alguma dúvida ou sugestão, por favor, entre em contato através do perfil no X/Twitter (@EconDataViz).