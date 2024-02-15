import os
from datetime import datetime
import pandas as pd
import yaml

from airflow import DAG
from collections import Counter
from airflow.operators.python import PythonOperator
from airflow.decorators import dag, task
from airflow.sensors.filesystem import FileSensor
from airflow.hooks.filesystem import FSHook


# global variable for airports file name
VOTES_FILE = 'votes.csv'

# list of flavors
flavors_choices = ["lemon","vanilla","chocolate","pistachio","strawberry","confetti","caramel","pumpkin","rose"]

# This task will read each row in the votes csv file and checks whether the value is in a given 
# list of flavor choices. If it is in the list then it appends it to a new list 
@task
def read_file():
    """
    read cake flavor votes file from a CSV

    This function uses an Airflow FileSystem Connection called "data_fs" as the root folder
    to look for the votes file. Make sure this FileSystem connection exists
    """
            
 # get the data_fs filesystem root path
    data_fs = FSHook(conn_id='data_fs')     # get airflow connection for data_fs
    data_dir = data_fs.get_path()           # get its root path
    print(f"data_fs root path: {data_dir}")

    # create the full path to the votes file
    file_path = os.path.join(data_dir, VOTES_FILE)
    print(f"reading file: {file_path}")
    
    valid_choices=[]
    # read csv
    df = pd.read_csv(file_path, header=1)
        
    for i in df['votes']:
        if i in flavors_choices:
            valid_choices.append(i)
    return valid_choices

# Create a task that takes the list from the previous task and prints the item that appears the most
@task
def tally_votes(valid_choices):
    # count how many times each flavor is in the list
    flavor_counts = Counter(valid_choices)
    
    #find the favorite flavor
    fav_flavor=flavor_counts.most_common(1)
    
    # print the item that appears the most
    print(f"fan favorite: {fav_flavor}")

    
@dag(
    schedule_interval="@once",
    start_date=datetime.utcnow(),
    catchup=False,
    default_view='graph',
    is_paused_upon_creation=True,
    tags=['votes', 'cake flavors'],
)
def file_sensor_dag():
    
    # define the file sensor...
    # wait for the votes file in the "data_fs" filesystem connection
    wait_for_file = FileSensor(
        task_id='wait_for_file',
        poke_interval=15,                   # check every 15 seconds
        timeout=(10 * 60),                  # timeout after 10 minutes
        mode='poke',                        # mode: poke, reschedule
        filepath = VOTES_FILE,        # file path to check (relative to fs_conn)
        fs_conn_id='data_fs',               # file system connection (root path)
    )

    # read the file
    read_file_task = read_file()
    tally_votes_task = tally_votes(read_file_task)
    
    # orchestrate tasks
    wait_for_file >> read_file_task >> tally_votes_task
# create the dag
dag = file_sensor_dag()