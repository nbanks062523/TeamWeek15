## Setup/Installation Requirements
In order to set this up, you will need to make a directory for your file and then switch over to that directory. Then, create a virtual environment for python 3 to work in. Change into your virtual environment using source venv/bin/activate. You will need to install the requirements.txt file

```
pip install -r requirements.txt
```

After creating your virtual environment in your project directory, you will need to make sure you have docker installed. The link to the different installation options can be found [here](https://docs.docker.com/engine/install/). Once you have docker up and running, you will need to allocate atleast 4gb worth of cpu memory to the airflow docker container. To do this:
- click the gear icon on the top right to go into Settings
- click the 'Resources' tab on the left 
- Set the Memory slider to at least 4GB as shown below, then click 'Apply & Restart':

Once docker is all set up, we have to set up a folder to contain our airflow files. In your project directory, create a folder called dsa-airflow. Using your CLI (command line interface), path into your dsa-airflow folder. Then, create a logs folder, plugins folder, a dags folder, and a config folder within your dsa-airflow folder.

```bash
mkdir -p ./dags ./logs ./plugins ./config
```

You also need to create a .env in your dsa-airflow folder using 

```bash
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

After completing this, you will need to fetch the docker yaml file into your dsa-airflow folder using 

```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml'
```

In this yaml file, you'll need to mount your local airflow directory to /opt/airflow. You'll also need to direct your data folder. You can add these in the yaml like this:

![Volumes](/images/yaml_volumes.png)

Once you have your dsa-airflow folder intact, you need to start airflow. in a bash terminal, navigate to this dsa-airflow directory. Use:

```bash
docker compose up airflow-init
```

This command runs database migrations (which moves data between databases), and creates a default user account with the login 'airflow' and the password 'airflow'. After this task has been completed (you should see an 'exited with code 0'), press ctrl+c while your CLI is open to stop airflow from running. 

Once initialized, we can start the rest of our containers with a simple

```bash
docker-compose up
```

When you have airflow running in your CLI, you will need to open a new terminal to perform any actions necessary using bash. 

Using these steps, you should have airflow talking to your local computer. In order to use the airflow UI, go to the URL [localhost:8080/home](localhost:8080/home). From here, type in your username 'airflow' and password 'airflow' to log into the airflow UI. In this interface, you will be able to run any DAGs you have created.

Now that we have airflow up and running, lets look at making a connection. In your UI, look at the bar to the right of the airflow logo in the upper left corner and go to Admin -> connections. This will take you to your connections directory. Here, you can click on the blue + button to create a connection. Name this connection whatever you'd like (I called mine data_fs) and set your path to the data folder within your dsa-airflow (create this folder if you need to). The path should be /data since you're already in your dsa-airflow folder. Then, press create. You should be able to use this connection to access your data folder in your dsa-airflow directory, allowing you to make a file sensor for the data file. 

When you need to power down airflow, navigate to your CLI with airflow running and press CTRL + C. This will stop airflow from running. Additionally, run the command docker system prune --volumes in order to delete the volumes you created using airflow.

An alternative way to power down airflow is to type 

```bash
docker compose down
```

in your usable CLI. 