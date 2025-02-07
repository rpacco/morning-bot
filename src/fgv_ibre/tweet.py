import tweepy
import os
import pandas as pd

def gen_text(df, title, emojis):
    tweet_text = f'{emojis} {title}, referência {df.index[-1].date().strftime("%m-%Y")}:\n\n'
    var_mom = df.pct_change(1).iloc[-1]
    var_yoy = (df.rolling(12).sum() / df.shift(12).rolling(12).sum() - 1).iloc[-1]
    df_merged = pd.concat([var_mom, var_yoy], axis=1).T
    df_merged.index = ['MoM', 'YoY']
    for col in df_merged.columns:
        tweet_text += f'-{col}:'
        for index, value in df_merged[col].items():
            tweet_text += (
                f' {value:.2%} {index};'
                f''
                )
        tweet_text += '\n'
    
    tweet_text += "\nFonte: @FGVIBRE"

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
    # print(media_id)

    # Send Tweet with Text and media ID
    client.create_tweet(text=text, media_ids=[media_id])
    print("Tweeted!")
