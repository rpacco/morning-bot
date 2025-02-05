import tweepy
import os


def text_juros(df, name):
    # Obtem os valores atuais
    valores_atuais = df.iloc[-1]

    # Obtem os valores do último mês
    valores_ultimo_mes = df.iloc[-2]

    # Obtem os valores de 1 ano atrás
    valores_1_ano_atras = df.iloc[-13]

    ref = df.index[-1].strftime('%m/%Y')

    # Cria o tweet
    tweet = f"{name}, referência {ref}:\n\n"
    for col in df.columns:
        valor_atual = valores_atuais[col]
        var_ultimo_mes = (valor_atual - valores_ultimo_mes[col]) * 100  # converte para basis points
        var_1_ano_atras = (valor_atual - valores_1_ano_atras[col]) * 100  # converte para basis points
        moM_emoji = "🔺" if var_ultimo_mes > 0 else "🔻" if var_ultimo_mes < 0 else ""
        yoY_emoji = "🔺" if var_1_ano_atras > 0 else "🔻" if var_1_ano_atras < 0 else ""
        tweet += f"{col}: {valor_atual:.2f}% (MoM: {moM_emoji}{var_ultimo_mes:.0f}bps, YoY: {yoY_emoji}{var_1_ano_atras:.0f}bps)\n"
    tweet += "\nFonte: @BancoCentralBR"

    return tweet

def text_credito(df, name):
    # Calcula a variação mensal
    df['Variação Mensal PJ'] = df['Pessoa Jurídica'].pct_change() * 100
    df['Variação Mensal PF'] = df['Pessoa Física'].pct_change() * 100
    
    # Calcula a variação acumulada em 12 meses
    df['Variação Acumulada 12M PJ'] = df['Pessoa Jurídica'].pct_change(periods=12) * 100
    df['Variação Acumulada 12M PF'] = df['Pessoa Física'].pct_change(periods=12) * 100
    
    # Pega as informações do último mês
    ultimo_mes = df.iloc[-1]
    
    # Cria o tweet
    tweet = (
        f"📊 {name}, referência: {ultimo_mes.name.strftime('%m/%Y')}\n\n"
        f"Valor Total: {ultimo_mes['Total']:.2f} Bi\n"
        f"PJ: {ultimo_mes['Pessoa Jurídica']:.2f} Bi\n"
        f"-Mensal: {'Alta' if ultimo_mes['Variação Mensal PJ'] > 0 else 'Baixa'} de {ultimo_mes['Variação Mensal PJ']:.2f}%\n"
        f"-Acumulado 12 meses: {'Alta' if ultimo_mes['Variação Acumulada 12M PJ'] > 0 else 'Baixa'} de {ultimo_mes['Variação Acumulada 12M PJ']:.2f}%\n"
        f"PF: {ultimo_mes['Pessoa Física']:.2f} Bi\n"
        f"-Mensal: {'Alta' if ultimo_mes['Variação Mensal PF'] > 0 else 'Baixa'} de {ultimo_mes['Variação Mensal PF']:.2f}%\n"
        f"-Acumulado 12 meses: {'Alta' if ultimo_mes['Variação Acumulada 12M PF'] > 0 else 'Baixa'} de {ultimo_mes['Variação Acumulada 12M PF']:.2f}%\n\n"
        "Fonte: @BancoCentralBR"
    )
    return tweet

def text_fiscais(df, name):
    ultima_data = df.index[-1].strftime('%m/%Y')
    mom_prim = df['MoM_prim'].iloc[-1]
    yoy_prim = df['YoY_prim'].iloc[-1]
    mom_int = df['MoM_int'].iloc[-1]
    yoy_int = df['YoY_int'].iloc[-1]

    if mom_prim > 0:
        mom_prim_str = f'+R${mom_prim:.2f} bi'
    else:
        mom_prim_str = f'-R${abs(mom_prim):.2f} bi'

    if yoy_prim > 0:
        yoy_prim_str = f'+R${yoy_prim:.2f} bi'
    else:
        yoy_prim_str = f'-R${abs(yoy_prim):.2f} bi'

    if mom_int > 0:
        mom_int_str = f'+R${mom_int:.2f} bi'
    else:
        mom_int_str = f'-R${abs(mom_int):.2f} bi'

    if yoy_int > 0:
        yoy_int_str = f'+R${yoy_int:.2f} bi'
    else:
        yoy_int_str = f'-R${abs(yoy_int):.2f} bi'

    tweet = (
        f'📊💵 {name}, referência {ultima_data}:\n\n'
        f'-Resultado primário mensal: {mom_prim_str}\n'
        f'-Juros nominais mensais: {mom_int_str}\n\n'
        f'-Resultado primário em 12 meses: {yoy_prim_str}\n'
        f'-Juros nominais em 12 meses: {yoy_int_str}\n\n'
        f'Fonte: @BancoCentralBR'
    )
    return tweet

def text_pct(df, name):
    tweet_text = f'## {name}, referência {df.index[-1].date().strftime("%m-%Y")}:\n\n'
    dict_var = {'YoY': 'em 12 meses', 'MoM': 'mensal'}
    for col, value in df.iloc[-1,].items():
        if value > 0:
            tweet_text += f"\U0001F4C8 Alta de {value:.2f}% {dict_var.get(col, col)}.\n"
        else:
            tweet_text += f"\U0001F4C9 Queda de {value:.2f}% {dict_var.get(col, col)}.\n"
            
    tweet_text += "\nFonte: @BancoCentralBR"

    return tweet_text

def text_cambio(df, name):
    monthly_data = df.resample('ME').sum().iloc[-12:]
    ref = df.index[-1]
    current_value = monthly_data.iloc[-1].values[0]
    accumulated_value = monthly_data.sum().values[0]
    # Start building the tweet text
    tweet_text = f'\U0001F4B8 {name}, referência {ref.date().strftime('%m/%Y')}:\n\n'
    
    # Current month's value text
    if current_value > 0:
        tweet_text += f"\U0001F7E2 Entrada de US$ {current_value:.2f} BI no mês.\n"
    else:
        tweet_text += f"\U0001F534 Saída de US$ {abs(current_value):.2f} BI no mês.\n"
    
    # Accumulated 12-month value text
    if accumulated_value > 0:
        tweet_text += f"\U0001F7E2 Acumulado 12 meses: entrada de US$ {accumulated_value:.2f} BI.\n"
    else:
        tweet_text += f"\U0001F534 Acumulado 12 meses: saída de US$ {abs(accumulated_value):.2f} BI.\n"
    
    # Add source information
    tweet_text += "\nFonte: @BancoCentralBR"
    
    return tweet_text

def text_credito_livredir(df, name):
    # Calcula a variação mensal
    df['Variação Mensal Direcionado'] = df['Direcionado'].pct_change() * 100
    df['Variação Mensal Livre'] = df['Livre'].pct_change() * 100
    
    # Calcula a variação acumulada em 12 meses
    df['Variação Acumulada 12M Direcionado'] = df['Direcionado'].pct_change(periods=12) * 100
    df['Variação Acumulada 12M Livre'] = df['Livre'].pct_change(periods=12) * 100
    
    # Pega as informações do último mês
    ultimo_mes = df.iloc[-1]
    
    # Cria o tweet
    tweet = (
        f"📊 {name}, referência: {ultimo_mes.name.strftime('%m/%Y')}\n\n"
        f"Valor Total: {ultimo_mes['Total']:.2f} Bi\n"
        f"\nDirecionado: {ultimo_mes['Direcionado']:.2f} Bi\n"
        f"-Mensal: {'Alta' if ultimo_mes['Variação Mensal Direcionado'] > 0 else 'Baixa'} de {ultimo_mes['Variação Mensal Direcionado']:.2f}%\n"
        f"-Acumulado 12 meses: {'Alta' if ultimo_mes['Variação Acumulada 12M Direcionado'] > 0 else 'Baixa'} de {ultimo_mes['Variação Acumulada 12M Direcionado']:.2f}%\n"
        f"\nLivre: {ultimo_mes['Livre']:.2f} Bi\n"
        f"-Mensal: {'Alta' if ultimo_mes['Variação Mensal Livre'] > 0 else 'Baixa'} de {ultimo_mes['Variação Mensal Livre']:.2f}%\n"
        f"-Acumulado 12 meses: {'Alta' if ultimo_mes['Variação Acumulada 12M Livre'] > 0 else 'Baixa'} de {ultimo_mes['Variação Acumulada 12M Livre']:.2f}%\n\n"
        "Fonte: @BancoCentralBR"
    )
    return tweet


def create_tweet(text, image_path, image_buffer):
    # Retrieve environment variables
    consumer_key = os.environ.get("CONSUMER_KEY")
    consumer_secret = os.environ.get("CONSUMER_SECRET")
    access_token = os.environ.get('ACCESS_TOKEN')
    access_secret = os.environ.get('ACCESS_SECRET')
    bearer_token = os.environ.get('BEARER_TOKEN')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth=auth, wait_on_rate_limit=True)

    client = tweepy.Client(
        consumer_key=consumer_key, 
        consumer_secret=consumer_secret, 
        access_token=access_token, 
        access_token_secret=access_secret , 
        bearer_token=bearer_token,
        wait_on_rate_limit=True
        )

    # Upload image to Twitter. Replace 'filename' your image filename.
    media_id = api.media_upload(filename=f"{image_path}", file=image_buffer).media_id_string
    
    # Send Tweet with Text and media ID
    client.create_tweet(text=text, media_ids=[media_id])
    print("Tweeted!")