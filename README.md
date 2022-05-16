# AIRFLOW

## Initializing Environment

Before starting Airflow for the first time, You need to prepare your environment, i.e. create the necessary files, directories and initialize the database.

## Setting the right Airflow user

On Linux, the quick-start needs to know your host user id and needs to have group id set to 0. Otherwise the files created in dags, logs and plugins will be created with root user. You have to make sure to configure them for the docker-compose:

mkdir -p ./dags ./logs ./plugins

echo -e "AIRFLOW_UID=$(id -u)" > .env

See Docker Compose environment variables

For other operating systems, you will get warning that AIRFLOW_UID is not set, but you can ignore it. You can also manually create the .env file in the same folder your docker-compose.yaml is placed with this content to get rid of the warning:

AIRFLOW_UID=50000

## Initialize the database
On all operating systems, you need to run database migrations and create the first user account. To do it, run.

docker-compose up airflow-init

After initialization is complete, you should see a message like below.

airflow-init_1       | Upgrades done
airflow-init_1       | Admin user airflow created
airflow-init_1       | 2.2.5
start_airflow-init_1 exited with code 0
The account created has the login airflow and the password airflow.

##  Cleaning-up the environment
The docker-compose we prepare is a "Quick-start" one. It is not intended to be used in production and it has a number of caveats - one of them being that the best way to recover from any problem is to clean it up and restart from the scratch.

The best way to do it is to:

Run docker-compose down --volumes --remove-orphans command in the directory you downloaded the docker-compose.yaml file

remove the whole directory where you downloaded the docker-compose.yaml file rm -rf '<DIRECTORY>'

re-download the docker-compose.yaml file

re-start following the instructions from the very beginning in this guide

## Running Airflow
Now you can start all services:

docker-compose up -d

ssh setup:

  ssh-keygen -t rsa -b 4096 -f ./id_rsa
  cp id_rsa ./plugins/devserver_sshprivatekey.pem


