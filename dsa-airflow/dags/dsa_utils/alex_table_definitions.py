
import time
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

# local module imports
from dsa_utils.alex_utils import logger, config


# setup the bigquery client
PROJECT_NAME = config['project']
DATASET_NAME = config['dataset']
# starting a variable name with _ is python convention to say 
# this is a private module variable and should not be imported outside of this module
_client: bigquery.Client = None


def get_client() -> bigquery.Client:
    """
    returns a bigquery client to the current project

    Returns:
        bigquery.Client: bigquery client
    """
    # check to see if the client has not been initialized
    global _client
    if _client is None:
        # initialize the client
        _client = bigquery.Client(project=PROJECT_NAME)
        logger.info(f"successfully created bigquery client. project={PROJECT_NAME}")
    return _client


# Define table schemas
# ---------------------------------
# Obesity rating table schema
OBESITY_TABLE_SCHEMA = [
    bigquery.SchemaField('state', 'STRING', mode='REQUIRED'),
    bigquery.SchemaField('state_abbrev', 'STRING', mode='NULLABLE'),
    bigquery.SchemaField('obesity_percentage', 'FLOAT', mode='NULLABLE'),
    bigquery.SchemaField('area_sq_mi', 'FLOAT', mode='NULLABLE'),
    bigquery.SchemaField('subway_count_per_state', 'FLOAT', mode='NULLABLE'),
    bigquery.SchemaField('chipotle_count_per_state', 'FLOAT', mode='NULLABLE'),
    bigquery.SchemaField('sq_mi_per_subway', 'FLOAT', mode='NULLABLE'),
    bigquery.SchemaField('sq_mi_per_chipotle', 'FLOAT', mode='NULLABLE'),
]

# subway store table schema
SUBWAY_TABLE_SCHEMA = [
    bigquery.SchemaField("name", 'STRING', mode='REQUIRED'),
    bigquery.SchemaField("street_address", 'STRING', mode='NULLABLE'),
    bigquery.SchemaField("city", 'STRING', mode='NULLABLE'),
    bigquery.SchemaField("state", 'STRING', mode='NULLABLE'),
    bigquery.SchemaField("zip_code", 'STRING', mode='NULLABLE'),
    bigquery.SchemaField("country", 'STRING', mode='NULLABLE'),
    bigquery.SchemaField("latitude", 'FLOAT', mode='NULLABLE'),
    bigquery.SchemaField("longitude", 'FLOAT', mode='NULLABLE'),
]

# chipotle store table schema
CHIPOTLE_TABLE_SCHEMA = [
    bigquery.SchemaField('state', 'STRING', mode='REQUIRED'),
    bigquery.SchemaField('location', 'STRING', mode='NULLABLE'),
    bigquery.SchemaField('address', 'STRING', mode='NULLABLE'),
    bigquery.SchemaField('latitude', 'STRING', mode='NULLABLE'),
    bigquery.SchemaField('longitude', 'INTEGER', mode='NULLABLE'),
]

# global dict to hold all table schemas
TABLE_SCHEMAS = {
    'obesity_rating': OBESITY_TABLE_SCHEMA,
    'subway_stores': SUBWAY_TABLE_SCHEMA,
    'chipotle_stores': CHIPOTLE_TABLE_SCHEMA,
}


def create_table(table_name: str) -> None:
    """
    Creates bigquery table. Table name must be one of the defined
    table schemas: obesity_table_schema, subway_table_schema, chipotle_table_schema

    Args:
        table_name (str): one of the following table names: obesity_rating, subway_stores, chipotle_stores
    """
    # raise an error if table name is not in one of our schemas
    assert table_name in TABLE_SCHEMAS, f"Table schema not found for table name: {table_name}"

    # full table id: project.dataset.table
    client = get_client()
    table_id = f"{PROJECT_NAME}.{DATASET_NAME}.{table_name}"
    # drop existing table if it exists
    try:
        table = client.get_table(table_id)      # table exists if this line doesn't raise exception
        client.delete_table(table)
        logger.info(f"dropped existed bigquery table: {table_id}")
        # wait a couple seconds before creating the table again
        time.sleep(2.0)
    except NotFound:
        # it's OK! table didn't exist
        pass
    # create the table
    schema = TABLE_SCHEMAS[table_name]
    table = bigquery.Table(table_id, schema=schema)
    table = client.create_table(table, exists_ok=False)
    logger.info(f"created bigquery table: {table_id}")
