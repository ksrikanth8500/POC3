CSV-to-PostgreSQL Data Pipeline Setup

This guide outlines the setup and execution of a data pipeline that ingests CSV files from Minio (S3-compatible storage), uses Airbyte for data ingestion, stores data in PostgreSQL, and leverages Prefect 2.x for data cleaning, transformation, and validation.
🚀 Step-by-Step Setup
1. Prerequisites
Ensure the following are installed:

Docker: For running Minio, Airbyte, and PostgreSQL services.
Python 3.9+: For running Prefect and Python scripts.
Prefect 2.x: For orchestrating the data pipeline.

Install required Python libraries:
pip install prefect pandas sqlalchemy psycopg2-binary

2. Start Services
Run the following command to start Minio, Airbyte, and PostgreSQL services using Docker Compose:
docker-compose up -d

Access the service consoles:

Minio Console: http://localhost:9000
Airbyte Console: http://localhost:8000

3. Service Configurations
Minio (S3-compatible Storage)

Access Key: minio_admin
Secret Key: minio_password
URL Endpoint: http://localhost:9000
Port: 9000

PostgreSQL Data Warehouse

Username: dwh
Password: dwh
External Host: localhost
External Port: 5455
Internal Host: postgres_dwh
Database Name: dwh
Default Schema: airbyte

Airbyte

Internal Host: host.docker.internal
Internal Host and Port: http://localhost:8000
User: airbyte
Password: password
Login: Provide a valid email when prompted.

4. Airbyte Configurations

Log in to Airbyte:

Open Airbyte at http://localhost:8000.
Enter a valid email and select Get started.


Set Up S3 Source:

Navigate to Sources in the left sidebar.
Search for S3 and select it.
Configure the S3 connection for customer data:
Source Name: S3_customer_information_cdc
Output Stream Name: daily_customer_information_cdc
Pattern of Files to Replicate: customer/*.csv
Bucket: raw
AWS Access Key ID: minio_admin
AWS Secret Access Key: minio_password
Path Prefix: customer/
Endpoint: http://host.docker.internal:9000


Scroll to the end and select Set up source.


Set Up PostgreSQL Destination:

Navigate to Destinations in the left sidebar.
Configure the PostgreSQL connection:
Destination Name: Postgres_DWH
Host: localhost
Port: 5455
Database Name: dwh
Default Schema: airbyte
User: dwh
Password: dwh


Scroll to the end and select Set up destination.


Create Connection:

Navigate to Connections in the left sidebar.
Select the S3_customer_information_cdc source.
Choose Use existing destination.
In the destination tab, select Postgres_DWH and confirm Use existing destination.



5. Prefect Flow for Data Processing
The following Prefect flow fetches data from the raw_data_1 table, cleans missing values, renames columns, validates the cleaned data, and stores the result in the processed_data_1 table in PostgreSQL.




6. Summary
This pipeline:

Ingests CSV files from Minio using Airbyte.
Stores raw data in PostgreSQL (raw_data_1 table).
Uses Prefect to fetch, clean, validate, and store the processed data in the processed_data_1 table.
Ensures a robust ETL process with error handling and validation.

Ensure all services are running and configurations are correct before executing the pipeline.
