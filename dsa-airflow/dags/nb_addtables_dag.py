import os
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.hooks.filesystem import FSHook
from airflow.operators.empty import EmptyOperator

# local imports
from dsa_utils.nb_utils import logger, config
from dsa_utils.nb_table_definitions import create_table, get_client
from dsa_utils.nb_table_loaders import load_table, DATA_FILES

######################### Checklist tasks ######################

# This task checks to make sure that the data files exist
def check_data_files():
    logger.info("checking data files")
    for filepath in DATA_FILES.values():
        print(filepath)
        if not os.path.exists(filepath):
            msg = f"Could not find source data file: {filepath}"
            logger.warn(msg)
            logger.warn("This is most likely because you haven't mounted the /data dir correctly in docker-compose.yaml. You must restart docker-compose after doing so.")
            raise FileNotFoundError(msg)

# This task checks to ensure a Big Query client connection can be established
def check_bigquery_client():
    # check if $GOOGLE_APPLICATION_CREDENTIALS is set
    google_app_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if (google_app_creds is None) or (not os.path.exists(google_app_creds)):
        logger.warn("GOOGLE_APPLICATION_CREDENTIALS is not set properly!")
        logger.warn("You most likely have not edited the docker-compose.yaml file correctly. You must restart docker-compose after doing so.")
    
    # Get client from dsa_utils.table_definitions module
    logger.info("checking bigquery client")
    client = get_client()
    location = client.location
    logger.info(f"bigquery client is good. bigquery location: {location}")

################################ Create DAG #########################################
with DAG(
    dag_id='load_food_data',
    schedule_interval='@once',
    start_date=datetime.utcnow(),
    catchup=False,
    default_view='graph',
    is_paused_upon_creation=True,
    tags=['dsa', 'data-loaders'],
    default_args={
        'depends_on_past': False,
        'email': ['airflow@example.com'],
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 0,
    }
) as dag:
    # dag's doc in markdown
    # setting it to this module's docstring defined at the very top of this file
    dag.doc_md = __doc__

    print(__file__)
    
# Execute tasks

# Checklist tasks
check_1 = PythonOperator(
        task_id='check_data_files',
        python_callable=check_data_files,
        doc_md=check_data_files.__doc__             # adding function docstring as task doc
    )
check_2 = PythonOperator(
        task_id='check_bigquery_client',
        python_callable=check_bigquery_client,
        doc_md=check_bigquery_client.__doc__        # adding function docstring as task doc
    )
# create an empty operator for branching the table creation tasks
    t1 = EmptyOperator(task_id='create_tables')
    table_names = ('food_inflation_BM', 'grocery_prices_BM','snap_poverty_pop','snap_population','snap_program_part')

# create a separate task for creating each table
    create_tasks = []
    for t in table_names:
        task = PythonOperator(
            task_id=f"create_{t}_table",
            python_callable=create_table,               # call the dsa_utils.table_definitions.create_table
            op_kwargs={'table_name': t},       # arguments to create_table() function
            doc_md=create_table.__doc__                 # take function docstring
        )
        create_tasks.append(task)

    # create another empty operator for branching table loading tasks
    t2 = EmptyOperator(task_id='load_files')

    # create a separate task for loading each table
    load_tasks = []
    for t in table_names:
        task = PythonOperator(
            task_id=f"load_{t}_table",
            python_callable=load_table,               # call the dsa_utils.table_loaders.load_table
            op_kwargs={'table_name': t},       # arguments to load_table() function
            doc_md=load_table.__doc__                 # take function docstring
        )
        load_tasks.append(task)

    # create empty task to branch back in
    done = EmptyOperator(task_id='done')

    check_1 >> check_2 >> t1 >> create_tasks >> t2 >> load_tasks >> done
