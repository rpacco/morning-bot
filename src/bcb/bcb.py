from datetime import datetime
from bcb import sgs


def get_bc_serie(series: list, name: str, colunas: list, reference: datetime.date, raw: bool = False, multiplicador: int = 1):
    dict_codes = dict(zip(colunas, series))
    try:
        df_merged = sgs.get(codes=dict_codes)
        df_merged.rename_axis('data', axis='index', inplace=True)
    except Exception as e:
        print(f"Error for series: {e}")
        return None
        
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
