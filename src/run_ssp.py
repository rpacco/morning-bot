from src.ssp.ssp import wrangle_data
from src.ssp.tweet import generate_tweet_text, create_tweet
from src.ssp.gen_viz import gen_viz
from utils.bucket_conn import update_logs_conn
from datetime import datetime


def run_ssp(logger, logs_df):
    logger.log_text("Starting SSP crawler", severity="INFO")
    name = 'roubos'

    if name in logs_df['indicator'].values:
        logger.log_text(f"Indicator already tweeted: {name}", severity="INFO")
        return 'SSP crawler already tweeted!'
    
    today = datetime.today().date()
    df = wrangle_data()
    if df.index[-1].date().month == (today.month + 12 - 1)%12:
        twt_txt = generate_tweet_text(df)
        chart = gen_viz(df)
        create_tweet(text=twt_txt, image_path=name, image_buffer=chart)
        chart.close()

        logger.log_text(f"Tweet created and sent for {name}", severity="INFO")
        logs_df.loc[len(logs_df)] = {"source": "ssp", "indicator": name, "posted": True}
        update_logs_conn(logs_df)
        return 'SSP crawler tweeted sucessfully!'
    else:
        logger.log_text("SSP data nao atualizado na fonte", severity="INFO")
        return "SSP data nao atualizado na fonte"
