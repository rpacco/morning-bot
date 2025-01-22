from datetime import datetime
from dateutil.relativedelta import relativedelta
from src.anfavea.anfa_calendar import check_release_date
from src.anfavea.anfa import get_xls_link, read_excel
from src.anfavea.tweet import twt_text, create_tweet
from src.anfavea.gen_viz import viz_anfavea
from utils.bucket_conn import update_logs_conn

def run_anfa(logger, logs_df):
    logger.log_text("Starting ANFAVEA scheduler crawler", severity="INFO")
    today = datetime.today().date()
    title = 'anfavea'

    if title in logs_df['indicator'].values:
        logger.log_text(f"Indicator already tweeted: {title}", severity="INFO")
        return (f"ANFAVEA Scheduler: 1 indicator already tweeted")

    release_date = check_release_date()
    if release_date == today:
        try:
            link = get_xls_link()
            df = read_excel(link)
            last_db_date = df.index[-1].month
            last_release_date = (today - relativedelta(months=1)).month
            if last_db_date == last_release_date:
                text = twt_text(df)
                img_buff = viz_anfavea(df)
                create_tweet(text=text, image_path=f"{title}", image_buffer=img_buff)
                img_buff.close()
                logger.log_text(f"Tweet created and sent for {title}", severity="INFO")
                logs_df.loc[len(logs_df)] = {"source": "anfavea", "indicator": title, "posted": True}
                update_logs_conn(logs_df)
                return (f"ANFAVEA Scheduler: 1 new indicator processed")
            else:
                logger.log_text(f"Data for {title} does not match expected month", severity="WARNING")
                return (f"ANFAVEA Scheduler: indicator not updated on source")
        except Exception as e:
            logger.log_text(f"Unexpected error while processing {title}: {str(e)}", severity="ERROR")
            return (f"ANFAVEA Scheduler: "
                    f"0 new indicators processed, "
                    f"1 error encountered, "
                    f"0 indicators already tweeted, "
                    f"0 indicators had no data from spider.")
    else:
        logger.log_text(f"Today is not the release date for {title}", severity="INFO")
        return (f"ANFAVEA Scheduler: No data to process")