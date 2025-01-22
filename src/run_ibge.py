import pandas as pd
from src.ibge.ibge import get_ibge_index
from src.ibge.ibge_sched import run_crawler
from src.ibge.gen_viz import wrangle, gen_chart
from src.ibge.tweet import gen_text, create_tweet
from utils.bucket_conn import update_logs_conn

def run_ibge(logger, logs_df):
    logger.log_text("Starting IBGE scheduler crawler", severity="INFO")

    df = run_crawler(logger=logger)

    if df is None or df.empty:
        logger.log_text("IBGE scheduler returned no data.", severity="WARNING")
        return "No IBGE data to process"

    df = df.apply(lambda x: x.map(lambda y: y.isoformat() if isinstance(y, pd.Timestamp) else y))

    processed_count = 0
    errors = []
    already_tweeted = []

    for index, row in df.iterrows():    
        name = row['name']
        if name in logs_df['indicator'].values:  # Check if the indicator is already logged
            logger.log_text(f"Indicator already tweeted: {name}", severity="INFO")
            already_tweeted.append(name)
            continue

        title = row['title']
        reference = pd.to_datetime(row['referencia'])
        table = row['table']
        v = row['v']
        d = row['d']
        subtitle = row['subtitle']
        
        logger.log_text(f"Running IBGE crawler for {name}", severity="INFO")
        try:
            df_raw = get_ibge_index(title, reference, table, v, d, name)
            df_clean = wrangle(df_raw)
            
            if df_clean.empty:
                logger.log_text(f"No data returned for cleaning for {name}", severity="WARNING")
                continue

            twt_text = gen_text(df_clean, f"{name}")
            chart = gen_chart(df_clean, name, subtitle)
            create_tweet(twt_text, image_path=f"{name}", image_buffer=chart)
            chart.close()
            
            logger.log_text(f"Tweet created and sent for {name}", severity="INFO")
            logs_df.loc[len(logs_df)] = {"source": "ibge", "indicator": name, "posted": True}
            update_logs_conn(logs_df)
            processed_count += 1
        except Exception as e:
            logger.log_text(f"Failed to process data of indicator: {name} - {str(e)}", severity="ERROR")
            errors.append(f"Failed to process data of indicator: {name} - {str(e)}")

    # Format the return value to handle multiple outcomes
    return (
        f"IBGE Scheduler: "
        f"Processed {processed_count} new indicators, "
        f"{errors} errors encountered, "
        f"{already_tweeted} indicators already tweeted, "
        )