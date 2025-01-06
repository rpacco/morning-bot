from google.cloud import storage
import pandas as pd
from datetime import datetime
import io

def logs_conn():
    today = datetime.today().date()
    client = storage.Client()

    bucket_name = 'tt-bot'
    file_name = f'tweeted-logs/{today}.csv'

    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    
    try:
        csv_content = blob.download_as_text()
        df = pd.read_csv(io.StringIO(csv_content))
    except Exception as e:
        print(f"File does not exist or an error occurred: {e}")
        df = pd.DataFrame(columns=["source", "indicator", "posted"])
        blob.upload_from_string(df.to_csv(index=False), content_type='text/csv')
        print(f"Created new CSV file: {file_name}")

    return df

def update_logs_conn(df):
    """
    Updates the CSV file in Google Cloud Storage with the provided DataFrame.

    :param df: pandas DataFrame to upload to GCS
    :return: None
    """
    today = datetime.today().date()
    client = storage.Client()

    bucket_name = 'tt-bot'
    file_name = f'tweeted-logs/{today}.csv'

    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)

    # Convert DataFrame to CSV string
    csv_data = df.to_csv(index=False)

    try:
        # Upload the DataFrame as a CSV file to GCS
        blob.upload_from_string(csv_data, content_type='text/csv')
        print(f"Updated tt_logs CSV file: {file_name}")

    except Exception as e:
        print(f"An error occurred while updating the tt logs CSV file: {e}")
