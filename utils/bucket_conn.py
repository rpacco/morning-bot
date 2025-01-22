from google.cloud import storage
import pandas as pd
from datetime import datetime, timedelta
import io

def logs_conn():
    today = datetime.today().date()
    client = storage.Client()

    bucket_name = 'tt-bot'
    file_name = f'tweeted-logs/{today.strftime("%Y-%m")}/{today}.csv'

    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    
    try:
        csv_content = blob.download_as_text()
        df = pd.read_csv(io.StringIO(csv_content))
    except Exception as e:
        print(f"File does not exist or an error occurred: {e}")
        df = pd.DataFrame(columns=["source", "indicator", "posted"])
        
        # Create the intermediate directory if it does not exist
        intermediate_dir = f'tweeted-logs/{today.strftime("%Y-%m")}/'
        bucket.blob(intermediate_dir).upload_from_string('', content_type='application/x-directory')
        
        blob.upload_from_string(df.to_csv(index=False), content_type='text/csv')
        print(f"Created new CSV file: {file_name}")

    return df

def logs_conn_monthly():
    today = datetime.today().date()
    client = storage.Client()

    bucket_name = 'tt-bot'
    bucket = client.get_bucket(bucket_name)

    # Initialize an empty DataFrame
    df_monthly = pd.DataFrame(columns=["source", "indicator", "posted"])

    # Get the prefix for the current month
    prefix = f'tweeted-logs/{today.strftime("%Y-%m")}/'

    # Create the intermediate directory if it does not exist
    intermediate_dir = prefix
    bucket.blob(intermediate_dir).upload_from_string('', content_type='application/x-directory')

    # Get a list of blobs in the bucket with the prefix
    blobs = list(bucket.list_blobs(prefix=prefix))

    # Loop through each blob
    for blob in blobs:
        try:
            csv_content = blob.download_as_text()
            df = pd.read_csv(io.StringIO(csv_content))
            df_monthly = pd.concat([df_monthly, df], ignore_index=True)
        except Exception as e:
            print(f"File does not exist or an error occurred: {e}")

    return df_monthly

def update_logs_conn(df):
    """
    Updates the CSV file in Google Cloud Storage with the provided DataFrame.

    :param df: pandas DataFrame to upload to GCS
    :return: None
    """
    today = datetime.today().date()
    client = storage.Client()

    bucket_name = 'tt-bot'
    file_name = f'tweeted-logs/{today.strftime("%Y-%m")}/{today}.csv'

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
