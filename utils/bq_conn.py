from google.cloud import bigquery
import pandas as pd
from datetime import datetime


def get_data_from_bq_table(project_id: str, dataset_id: str, table_id: str, query: str = None, sort_by_date: bool = True):
    """
    Retrieve data from a BigQuery table. If a query is provided, it will be used to fetch data.
    Otherwise, all data from the table will be returned.

    :param project_id: The ID of the project where the dataset resides.
    :param dataset_id: The ID of the dataset containing the table.
    :param table_id: The ID of the table to query.
    :param query: Optional SQL query string. If None, all data from the table is fetched.
    :return: List of dictionaries representing rows from the table.
    """
    client = bigquery.Client(project=project_id)
    if query is None:
        base_query = f"SELECT * FROM `{project_id}.{dataset_id}.{table_id}`"
        query = base_query + " ORDER BY date ASC" if sort_by_date else base_query
    
    try:
        # Execute the query
        query_job = client.query(query)
        # Convert the result directly to a DataFrame
        df = query_job.to_dataframe()
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', drop=True, inplace=True)
        df.dropna(inplace=True, how='any')
        return df
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()

def upsert_bq_table(project_id: str, dataset_id: str, table_id: str, data: list[dict]):
    client = bigquery.Client()
    
    table_id = f"{project_id}.{dataset_id}.{table_id}"  # Replace with your actual table identifier
    
    for row in data:
        try:
            query = f"""
            MERGE `{table_id}` T
            USING (SELECT @date AS date, @diesel_pct AS diesel_pct, @diesel_brl AS diesel_brl, 
                          @gasolina_pct AS gasolina_pct, @gasolina_brl AS gasolina_brl) S
            ON T.date = S.date
            WHEN MATCHED THEN
              UPDATE SET
                diesel_pct = S.diesel_pct,
                diesel_brl = S.diesel_brl,
                gasolina_pct = S.gasolina_pct,
                gasolina_brl = S.gasolina_brl
            WHEN NOT MATCHED THEN
              INSERT (date, diesel_pct, diesel_brl, gasolina_pct, gasolina_brl)
              VALUES (S.date, S.diesel_pct, S.diesel_brl, S.gasolina_pct, S.gasolina_brl)
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("date", "DATE", row['date']),
                    bigquery.ScalarQueryParameter("diesel_pct", "FLOAT", row['diesel_pct']),
                    bigquery.ScalarQueryParameter("diesel_brl", "FLOAT", row['diesel_brl']),
                    bigquery.ScalarQueryParameter("gasolina_pct", "FLOAT", row['gasolina_pct']),
                    bigquery.ScalarQueryParameter("gasolina_brl", "FLOAT", row['gasolina_brl']),
                ]
            )
            
            query_job = client.query(query, job_config=job_config)
            query_job.result()  # Wait for the job to complete and get results
            
            print(f"Successfully processed data for date: {row['date']}")

        except Exception as e:
            print(f"An error occurred while processing data for date {row['date']}: {str(e)}")
