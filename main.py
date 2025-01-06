from utils.bucket_conn import logs_conn, update_logs_conn
from run_fgv import run_fgv_scheduler
from run_ibge import run_ibge
from run_bcb import run_bcb
from run_ppi import run_ppi
from google.cloud import logging as gcp_logging

# Set up Google Cloud Logging
client = gcp_logging.Client()
logger = client.logger('main_run') 

def main_run(request):
    logger.log_text(f"Starting main_run function execution", severity="INFO")
    log_posts_df = logs_conn()
    result_fgv = run_fgv_scheduler(logger, log_posts_df)
    result_ibge = run_ibge(logger, log_posts_df)
    result_bcb = run_bcb(log_posts_df, logger)
    result_abicom = run_ppi(logger, log_posts_df)

    if isinstance(result_fgv, tuple):
        result_fgv = " ".join(result_fgv) if all(isinstance(item, str) for item in result_fgv) else str(result_fgv)
    
    if isinstance(result_ibge, tuple):
        result_ibge = " ".join(result_ibge) if all(isinstance(item, str) for item in result_ibge) else str(result_ibge)

    if isinstance(result_bcb, tuple):
        result_bcb = " ".join(result_bcb) if all(isinstance(item, str) for item in result_bcb) else str(result_bcb)
    
    if isinstance(result_bcb, tuple):
        result_abicom = " ".join(result_abicom) if all(isinstance(item, str) for item in result_abicom) else str(result_abicom)

    

    return result_fgv + "\n" + result_ibge + "\n" + result_bcb + "\n" + result_abicom