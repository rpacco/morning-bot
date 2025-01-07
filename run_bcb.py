import pandas as pd
from src.bcb.bcb_sched import bcb_calendar
from src.bcb.bcb import get_bc_serie
from src.bcb.tweet import text_fiscais, text_pct, create_tweet
from src.bcb.gen_viz import viz_fiscais, viz_pct
from utils.bucket_conn import update_logs_conn


def run_bcb(logs_df, logger = None):
    viz_functions = {
        "viz_fiscais": viz_fiscais,
        "viz_pct": viz_pct
    }

    txt_functions = {
        "text_fiscais": text_fiscais,
        "text_pct": text_pct
    }
    logger.log_text("Starting BCB scheduler crawler", severity="INFO")

    cat_bcb = pd.read_json('src/bcb/cat_bcb.json')

    try:
        calendar_df = bcb_calendar('mes', logger=logger)
        if calendar_df is not None:
            df = calendar_df.merge(cat_bcb, on='evento')
        else:
            logger.log_text("BCB calendar returned None", severity="WARNING")
            df = pd.DataFrame()  # Empty DataFrame if calendar_df is None
    except Exception as e:
        logger.log_text(f"Error fetching or merging BCB calendar: {str(e)}", severity="ERROR")
        df = pd.DataFrame()  # Empty DataFrame if an exception occurs

    if df.empty:
        logger.log_text("BCB scheduler returned no data.", severity="WARNING")
        return "No BCB data to process"

    df = df.apply(lambda x: x.map(lambda y: y.isoformat() if isinstance(y, pd.Timestamp) else y))

    processed_count = 0
    errors = []
    already_tweeted = []

    for index, row in df.iterrows():    
        name = row['category']
        if name in logs_df['indicator'].values:  # Check if the indicator is already logged
            logger.log_text(f"Indicator already tweeted: {name}", severity="INFO")
            already_tweeted.append(name)
            continue

        reference = pd.to_datetime(row['descricao'])
        series = row['series']
        mult = row['multiplicador']
        colunas = row['colunas']
        raw = row['raw']
        chart = row['chart']
        text = row['text']
        
        logger.log_text(f"Running BCB crawler for {name}", severity="INFO")
        try:
            df = get_bc_serie(series, name, colunas, reference, raw, mult)
            
            if df is None or not isinstance(df, pd.DataFrame) or df.empty or df.isna().all().all():
                logger.log_text(f"No valid DataFrame returned for cleaning for {name}", severity="WARNING")
                continue

            gen_text = txt_functions.get(text)
            gen_viz_bcb = viz_functions.get(chart)
            twt_text = gen_text(df, name)
            chart = gen_viz_bcb(df, name)
            create_tweet(twt_text, image_path=f"{name}", image_buffer=chart)
            chart.close()
            
            logger.log_text(f"Tweet created and sent for {name}", severity="INFO")
            logs_df.loc[len(logs_df)] = {"source": "bcb", "indicator": name, "posted": True}
            update_logs_conn(logs_df)
            processed_count += 1
        except Exception as e:
            logger.log_text(f"Failed to process data of indicator: {name} - {str(e)}", severity="ERROR")
            errors.append(f"Failed to process data of indicator: {name} - {str(e)}")

    return (
        f"BCB Scheduler: "
        f"Processed {processed_count} new indicators, "
        f"{len(errors)} errors encountered, "
        f"{len(already_tweeted)} indicators already tweeted."
    )