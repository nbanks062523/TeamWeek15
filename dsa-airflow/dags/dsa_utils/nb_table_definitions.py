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

# Food Inflation Rates by Month
FOODINFLATION_SCHEMA = [
    bigquery.SchemaField('Year', 'INTEGER',mode='NULLABLE'),
    bigquery.SchemaField('Jan', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('Feb', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('Mar', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('Apr', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('May', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('Jun', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('Jul', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('Aug', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('Sep', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('Oct', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('Nov', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('Dec', 'INTEGER', mode='NULLABLE'),
    ,
]

# Monthly Grocery Prices by State
MGROCPRICES_SCHEMA = [
    bigquery.SchemaField('Rank', 'INTEGER',mode='NULLABLE'),
    bigquery.SchemaField('State', 'STRING', mode='NULLABLE'),
    bigquery.SchemaField('City', 'STRING', mode='NULLABLE'),
    bigquery.SchemaField('Analyzed Population', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('Average Monthly Cost of Groceries Per Person', 'STRING', mode='NULLABLE'),
    bigquery.SchemaField('state_abbrev', 'STRING', mode='NULLABLE'),
    ,
]

# SNAP Poverty numbers by Year
SNAPPOV_SCHEMA = [
    bigquery.SchemaField('Record ID', 'INTEGER',mode='NULLABLE'),
    bigquery.SchemaField('State_CD', 'STRING', mode='NULLABLE'),
    bigquery.SchemaField('2006', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('2007', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('2010', 'INTEGER', mode='NULLABLE'),
    ,
]

# SNAP Population numbers by Year
SNAPPOP_SCHEMA = [
    bigquery.SchemaField('Record ID','INTEGER',mode='NULLABLE'),
    bigquery.SchemaField('State_CD','STRING', mode='NULLABLE'),
    bigquery.SchemaField('2005', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('2006', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('2007', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('2008', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('2009', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('2010', 'INTEGER', mode='NULLABLE'),
    ,
]

# SNAP Program Participants by Year
SNAPPRGPart_SCHEMA = [
    bigquery.SchemaField('Record ID','INTEGER',mode='NULLABLE'),
    bigquery.SchemaField('State_CD','STRING', mode='NULLABLE'),
    bigquery.SchemaField('2005', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('2006', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('2007', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('2008', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('2009', 'INTEGER', mode='NULLABLE'),
    bigquery.SchemaField('2010', 'INTEGER', mode='NULLABLE'),
    ,
]

# global dictionary to hold all table schemas
TABLE_SCHEMAS = {
    'food_inflation_BM': FOODINFLATION_SCHEMA,
    'grocery_prices_BM': MGROCPRICES_SCHEMA,
    'snap_poverty_pop': SNAPPOV_SCHEMA,
    'snap_population': SNAPPOP_SCHEMA,
    'snap_program_part': SNAPPRGPart_SCHEMA,
}


def create_table(table_name: str) -> None:
    """
    This section will create the bigquery tables

    Args:
        table_name (str): one of the following table names: 'food_inflation_BM','grocery_prices_BM','snap_poverty_pop','snap_population', 'snap_program_part'
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
        # Table doesn't exist
        pass
    
    # create the table
    schema = TABLE_SCHEMAS[table_name]
    table = bigquery.Table(table_id, schema=schema)
    table = client.create_table(table, exists_ok=False)
    logger.info(f"created bigquery table: {table_id}")