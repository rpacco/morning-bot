import tweepy
import os


def text_fiscais(df, name):
    tweet_text = f'## {name}, referência {df.index[-1].date().strftime("%m-%Y")}:\n\n'
    dict_var = {'MoM': 'Mensal', 'YoY': 'Últimos 12 meses'}
    for col, value in df.iloc[-1,].items():
        tweet_text += f"# {dict_var[col]} = {value/1000:.2f} BI\n"
            
    tweet_text += "\nFonte: @BancoCentralBR"

    return tweet_text

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