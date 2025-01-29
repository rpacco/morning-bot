import tweepy
import os

def twt_text(df):
    stats_dict = {}
    for col in df.columns:    
        stats_dict[col] ={
            'MoM': df[col].pct_change().iloc[-1], 
            'YoY': ((df[col].rolling(12).sum() / df[col].shift(12).rolling(12).sum()) - 1).iloc[-1]
        }

    # Initialize the tweet text
    tweet_texts = [f'\U0001F697 Resultados ANFAVEA, referência {df.index[-1].strftime('%m/%Y')}:\n\n']

    # Loop through the categories
    categories = {
        'Licenciamento': ['Licenciamento Total', 'Licenciamento Nacionais', 'Licenciamento Importados'],
        'Indústria Nacional': ['Produção', 'Exportação']
    }

    for category, keys in categories.items():
        # Add the category header
        tweet_texts.append(f'## {category}\n')

        # Loop through the keys in the category
        for key in keys:
            # Get the stats for the key
            stats = stats_dict[key]

            # Format the percentages to 1 decimal place for readability
            mom_percent = f"{stats['MoM'] * 100:.1f}%"
            yoy_percent = f"{stats['YoY'] * 100:.1f}%"

            # Determine if the change is positive or negative for better context in the tweet
            mom_direction = "alta" if stats['MoM'] >= 0 else "queda"
            yoy_direction = "Alta" if stats['YoY'] >= 0 else "Queda"

            # Construct the tweet text
            tweet = f'# {key.replace("Licenciamento ", "")}: {mom_direction} {mom_percent} mensal. {yoy_direction} de {yoy_percent} em 12 meses.\n'

            # Add the tweet text to the list
            tweet_texts.append(tweet)

        # Add a newline after each category
        tweet_texts.append('\n')

    # Join the tweet texts into a single string
    text = ''.join(tweet_texts)

    # Remove the trailing newline
    text = text.strip()

    return text


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