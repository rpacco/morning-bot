import tweepy
import os


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
    monthly_data = df.resample('ME').sum().iloc[-13:]
    ref = df.index[-1]
    tweet_text = f'\U0001F4B8 {name}, até {ref.date().strftime("%d-%m-%Y")}:\n\n'
    value = monthly_data.iloc[-1].values[0]
    if value > 0:
            tweet_text += f"\U0001F7E2 Entrada de US$ {value:.2f} BI.\n"
    else:
        tweet_text += f"\U0001F534 Saída de US$ {value:.2f} BI.\n"
            
    tweet_text += "\nFonte: @BancoCentralBR"


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