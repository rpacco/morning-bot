import pandas as pd
from src.fgv_ibre.fgv_ibre import FGVSpider
from src.fgv_ibre.fgv_sched import run_crawler
from src.fgv_ibre.gen_viz import chart_viz
from src.fgv_ibre.tweet import gen_text, create_tweet
from utils.bucket_conn import update_logs_conn

def run_fgv_scheduler(logger, logs_df):
    logger.log_text("Starting FGV scheduler crawler", severity="INFO")

    df = run_crawler(logger=logger)

    if df is None or df.empty:
        logger.log_text("FGV scheduler returned no data.", severity="WARNING")
        return "No FGV data to process"

    df = df.apply(lambda x: x.map(lambda y: y.isoformat() if isinstance(y, pd.Timestamp) else y))

    processed_count = 0
    error_count = 0
    already_tweeted = 0
    spider_no_data = 0

    for _, row in df.iterrows():    
        title = row['title']
        if title in logs_df['indicator'].values:  # Check if the indicator is already logged
            logger.log_text(f"Indicator already tweeted: {title}", severity="INFO")
            already_tweeted += 1
            continue

        codes = row['codes']
        ct_titles = row['meta']
        sched_time = f'{row["hora"][0]} {row["hora"][-1] if row["hora"][-1] else 0}'
        ref_date = pd.to_datetime(row['reference']).date()

        logger.log_text(f"Running FGVSpider for {title} at {sched_time}", severity="INFO")
        try:
            spider = FGVSpider(serie=codes, columns=ct_titles, logger=logger, ref_date=ref_date)
            result_df = spider.run()
            if result_df is None or result_df.empty:
                logger.log_text(f"Spider returned no data for {title}", severity="WARNING")
                spider_no_data += 1
                continue

            try:
                twt_text = gen_text(result_df, title)
                img_buff = chart_viz(result_df, title, logger)
                create_tweet(text=twt_text, image_path=f"{title}", image_buffer=img_buff)
                img_buff.close()
                logger.log_text(f"Tweet created and sent for {title}", severity="INFO")
                logs_df.loc[len(logs_df)] = {"source": "fgv", "indicator": title, "posted": True}
                update_logs_conn(logs_df)
                processed_count += 1
            except Exception as e:
                logger.log_text(f"Failed to tweet data of indicator: {title} - {str(e)}", severity="ERROR")
                error_count += 1
        except Exception as e:
            logger.log_text(f"Unexpected error while processing {title}: {str(e)}", severity="ERROR")
            error_count += 1

    # Here we return a summary of the processing results
    return (f"FGV Scheduler: "
            f"Processed {processed_count} new indicators, "
            f"{error_count} errors encountered, "
            f"{already_tweeted} indicators already tweeted, "
            f"{spider_no_data} indicators had no data from spider.")