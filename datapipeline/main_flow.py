from prefect import flow, task, get_run_logger
import pandas as pd
from sqlalchemy import create_engine
import json

# Create SQLAlchemy engine with explicit search_path to airbyte schema
engine = create_engine(
    "postgresql+psycopg2://dwh:dwh@localhost:5455/dwh?options=-csearch_path%3Dairbyte"
)

@task
def fetch_raw_data():
    logger = get_run_logger()
    try:
        df = pd.read_sql('SELECT * FROM airbyte."_airbyte_raw_import_postgrsql";', con=engine)
        logger.info(f"Fetched {len(df)} rows from raw_data_1")
        return df
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise

@task
def clean_data(df):
    logger = get_run_logger()
    cleaned_df = df.dropna()
    logger.info(f"Dropped rows with NA. Remaining rows: {len(cleaned_df)}")
    return cleaned_df

@task
def flatten_airbyte_data(df):
    logger = get_run_logger()
    try:
        # Flatten the '_airbyte_data' column, assuming it's a dictionary in each row
        df_airbyte_data = pd.json_normalize(df['_airbyte_data'])
        # Drop the original '_airbyte_data' column
        df = df.drop(columns=['_airbyte_data'])
        # Concatenate the flattened columns back into the DataFrame
        df = pd.concat([df, df_airbyte_data], axis=1)
        logger.info(f"Flattened _airbyte_data. New columns: {df.columns.tolist()}")
        return df
    except Exception as e:
        logger.error(f"Error flattening _airbyte_data: {e}")
        raise

@task
def transform_data(df):
    logger = get_run_logger()
    df.columns = [col.replace(" ", "$") for col in df.columns]
    logger.info(f"Transformed column names: {df.columns.tolist()}")
    return df

@task
def validate(df):
    logger = get_run_logger()
    if df.empty:
        logger.error("DataFrame is empty after cleaning!")
        raise ValueError("DataFrame is empty after cleaning!")
    logger.info("Validation passed.")
    return df

@task
def save_clean_data(df):
    logger = get_run_logger()
    try:
        # Ensure any dictionary columns are serialized as JSON strings
        for col in df.select_dtypes(include='object').columns:
            if isinstance(df[col].iloc[0], dict):
                df[col] = df[col].apply(json.dumps)

        df.to_sql("processed_data_1", engine, index=False, if_exists="replace")
        logger.info("Saved processed data to 'processed_data_1'")
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        raise

@flow(name="data-pipeline-flow")
def data_pipeline_flow():
    df = fetch_raw_data()
    cleaned = clean_data(df)
    flattened = flatten_airbyte_data(cleaned)
    transformed = transform_data(flattened)
    validated = validate(transformed)
    save_clean_data(validated)

if __name__ == "__main__":
    data_pipeline_flow()
