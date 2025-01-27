import pandas as pd
import os
import tweepy


def generate_tweet_text(data):
    # Convert 'date' to datetime for sorting and comparison
    data = data.reset_index()
    data['date'] = pd.to_datetime(data['date'])
    data = data.sort_values('date')

    # Calculate monthly variation
    data['monthly_variation_estado'] = data['estado'].pct_change() * 100
    data['monthly_variation_capital'] = data['capital'].pct_change() * 100
    
    # Calculate 12-month cumulative sum for estado and capital
    data['cum_sum_estado'] = data['estado'].rolling(window=12).sum()
    data['cum_sum_capital'] = data['capital'].rolling(window=12).sum()
    
    # Calculate 12-month cumulative variation
    data['cum_variation_estado'] = (data['cum_sum_estado'] / data['cum_sum_estado'].shift(12) - 1) * 100
    data['cum_variation_capital'] = (data['cum_sum_capital'] / data['cum_sum_capital'].shift(12) - 1) * 100
    
    # Get the latest data
    latest = data.iloc[-1]
    last_mom_estado = latest['monthly_variation_estado']
    last_mom_capital = latest['monthly_variation_capital']
    last_yoy_estado = latest['cum_variation_estado']
    last_yoy_capital = latest['cum_variation_capital']
    
    # Format the tweet text
    tweet_text = (
        f"\U0001F694\U0001F6A8 Total de roubos (estado de SP), referência {latest['data']}:\n"
        f"\n## Estado: {latest['estado']} casos\n"
        f"{'\U0001F53A Alta de' if last_mom_estado > 0 else '\U0001F53B Queda de'} {last_mom_estado:.2f}% mensal\n"
        f"{'\U0001F53A Alta de' if last_yoy_estado > 0 else '\U0001F53B Queda de'} {last_yoy_estado:.2f}% acumulado 12 meses\n"
        f"## Capital: {latest['capital']} casos\n"
        f"{'\U0001F53A Alta de' if last_mom_capital > 0 else '\U0001F53B Queda de'} {last_mom_capital:.2f}% mensal\n"
        f"{'\U0001F53A Alta de' if last_yoy_capital > 0 else '\U0001F53B Queda de'} {last_yoy_capital:.2f}% acumulado 12 meses\n"
    )
    tweet_text += '\nFonte: @SegurancaSP.'

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