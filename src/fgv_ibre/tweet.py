import tweepy
import os

def gen_text(df):
    columns_lower = [x.lower() for x in df.columns]
    if any('pib' in col for col in columns_lower):
        tweet_text = f'## {df.name}, referência {df.index[-1].date().strftime("%m-%Y")}:\n'
        var_mom = df.pct_change(1).iloc[-1]
        var_yoy = ((df.rolling(12).sum() / df.shift(12).rolling(12).sum()) - 1)*100
        if var_mom > 0:
            tweet_text += f"\U0001F4C8 Alta de {var_mom:.2%} M/M.\n"
        else:
            tweet_text += f"\U0001F4C9 Queda de {var_mom:.2%} M/M.\n"
        if var_yoy > 0:
            tweet_text += f"\U0001F4C8 Alta de {var_yoy:.2%} em 12 meses.\n"
        else:
            tweet_text += f"\U0001F4C9 Queda de {var_yoy:.2%} em 12 meses.\n"
        
        tweet_text += "\nFonte: @FGVIBRE"

    else:
        var_mm = df.pct_change().iloc[-1,:].sort_values(ascending=False)
        # Assuming df and var_mm are already defined
        tweet_text = f'## {df.name}, referência {df.index[-1].date().strftime("%m-%Y")}:\n'
        for col, value in var_mm.items():
            if value > 0:
                tweet_text += f"\U0001F4C8 {col.strip()}, alta de {value:.2%} M/M.\n"
            else:
                tweet_text += f"\U0001F4C9 {col.strip()}, queda de {value:.2%} M/M.\n"
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
