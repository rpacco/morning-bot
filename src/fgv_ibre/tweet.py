import tweepy
import os
import pandas as pd

def gen_text(df, title, emojis):
    # Última data da série
    ref_date = df.index[-1].strftime("%m-%Y")
    tweet = f"{emojis} {title} ({ref_date})\n\n"

    # Variações
    var_mom = df.pct_change(1).iloc[-1]
    var_yoy = (df.rolling(12).sum() / df.shift(12).rolling(12).sum() - 1).iloc[-1]

    # Função para emoji de tendência
    def trend_emoji(val):
        return "📈" if val > 0 else "📉" if val < 0 else "➡️"

    # Monta o texto linha por linha
    for col in df.columns:
        mom = var_mom[col]
        yoy = var_yoy[col]
        tweet += (
            f"{col}:\n"
            f"• MoM: {mom:+.1%} {trend_emoji(mom)}\n"
            f"• YoY: {yoy:+.1%} {trend_emoji(yoy)}\n"
        )

    tweet += "\nFonte: @FGVIBRE"
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
    # print(media_id)

    # Send Tweet with Text and media ID
    client.create_tweet(text=text, media_ids=[media_id])
    print("Tweeted!")
