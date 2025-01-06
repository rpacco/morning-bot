import pandas as pd


def get_ibge_index(indicador, referencia, table, v, d, name):
    """
    Retrieves and processes IBGE (Brazilian Institute of Geography and Statistics) index data from the API.

    Parameters:
        index (str): The index key specifying the data to retrieve. Valid options are described on file 'ibge_data_dictionary.md'.

    Returns:
        pandas.DataFrame: Processed index data with two columns: 'valor' (numeric values) and 'ano_mes' (datetime values).
                          The 'ano_mes' column is set as the index of the DataFrame.
    """
    # setting url endpoint
    url = (
    "https://apisidra.ibge.gov.br/values/"
    f"t/{table}/"
    "n1/all/"
    f"v/{v}/"
    f"p/all/{d}"
    )
    # Read JSON data from the API endpoint
    df = pd.read_json(url)[ ["V", "D3C", "D2N"] ]
    df = df[1:].rename(columns={'V': 'valor', 'D3C': 'ano_mes'})
    #Converting columns formatting
    df["ano_mes"] = pd.to_datetime(df["ano_mes"], format="%Y%m")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce", downcast='float')
    # Drop rows with missing values. Set 'ano_mes' column as the DataFrame index
    df.dropna(inplace=True)  
    df.set_index("ano_mes", drop=True, inplace=True)
    df = df.pivot_table(index=df.index, columns='D2N', values='valor', aggfunc='first').dropna()

    # return df
    if df.index[-1].date() == referencia.date():
        return df
    else:
        print('Dados não atualizados na fonte')
        return None
