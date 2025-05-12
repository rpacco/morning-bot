from src.abicom.ppi import PpiCrawler
from src.abicom.gen_viz import gen_text, gen_graph
from src.abicom.tweet import create_tweet
from utils.bq_conn import get_data_from_bq_table, upsert_bq_table
from utils.bucket_conn import update_logs_conn
from datetime import datetime, timedelta
import pandas as pd
import os

def run_ppi(logger, logs_df):
    logger.log_text("Starting ABICOM PPI crawler", severity="INFO")

    PROJECT_ID = os.environ.get('PROJECT_ID')
    DATASET_ID = os.environ.get('DATASET_ID')
    TABLE_ID = os.environ.get('TABLE_ID')
    
    combs = ['diesel_pct', 'gasolina_pct']
    already_tweeted = []
    for comb in combs:
        if comb in logs_df['indicator'].values:
            logger.log_text(f"Indicator already tweeted: {comb}", severity="INFO")
            already_tweeted.append(comb)
            continue

    if len(already_tweeted) == len(combs):
        logger.log_text("ABICOM PPI data already tweeted", severity="INFO")
        return "ABICOM PPI data already tweeted"
    
    today = datetime.today().date()
    start_date = today - timedelta(5)
    crawler = PpiCrawler(start_date)
    data = crawler.run()
    
    if data is None:
        logger.log_text("ABICOM PPI crawler returned no data.", severity="WARNING")
        return "No ABICOM PPI data to process"

    df_raw = get_data_from_bq_table(project_id=PROJECT_ID, dataset_id=DATASET_ID, table_id=TABLE_ID)
    df_new = pd.DataFrame(data)
    df_new.set_index('date', inplace=True)
    df_new.index = pd.to_datetime(df_new.index)
    df_updated = df_new.combine_first(df_raw).dropna()
    
    processed_count = 0
    errors = []

    for comb in combs:
        if comb in already_tweeted:
            continue

        try:
            if df_updated.empty or df_updated.index[-1].date() != today:
                logger.log_text("No new or updated data available.", severity="WARNING")
                continue

            df = df_updated.copy()
            df.to_csv('abicom_20250512.csv')
            if df.empty:
                logger.log_text(f"No data returned for cleaning for {comb}", severity="WARNING")
                continue

            twt_txt = gen_text(df, comb)
            chart = gen_graph(df, comb)
            create_tweet(text=twt_txt, image_path=comb, image_buffer=chart)
            chart.close()

            logger.log_text(f"Tweet created and sent for {comb}", severity="INFO")
            logs_df.loc[len(logs_df)] = {"source": "abicom", "indicator": comb, "posted": True}
            update_logs_conn(logs_df)
            processed_count += 1
        except Exception as e:
            logger.log_text(f"Failed to process data of indicator: {comb} - {str(e)}", severity="ERROR")
            errors.append(f"Failed to process data of indicator: {comb} - {str(e)}")
    
    if processed_count == 2:
        upsert_bq_table(PROJECT_ID, DATASET_ID, TABLE_ID, data)

    # Format the return value to handle multiple outcomes
    return (
        f"ABICOM PPI Scheduler: "
        f"Processed {processed_count} new indicators, "
        f"{len(errors)} errors encountered, "
        f"{len(already_tweeted)} indicators already tweeted"
    )