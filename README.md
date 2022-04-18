# How to Run Metaflow with Airflow on Minikube


# Setting Metaflow and Airflow with Minikube

TLDR; In order to run metaflow flows with airflow on minikube the following is required: 

1. [Setup, helm, minikube, and dag folder mount points in the minikube cluster](#setup-helm-and-minikube)
2. [Setup Metaflow and airflow on the minikube cluster](#setup-metaflow-and-airflow-in-minikube-cluster)
3. [Running authentication and metaflow related configurations](#setting-up-auth-and-metaflow-configurations)
    1. [Setup Kubernetes related secrets for AWS](#authentication-setup)
    2. [Setup metaflow related configuration](#metaflow-configuration-setup)
    3. [Run a test flow after setting up above configuration](#creating-a-test-airflow-dag-from-a-metaflow-flow)
    4. Accessing [Airflow](#getting-access-to-airflow-ui) and [Metaflow UI](#getting-access-to-metaflow-ui)
    5. TODO: Metaflow Results Access

## Setup Helm and Minikube

1. `brew install minikube helm`
2. Start minikube with a certain number of resources:`minikube start --cpus 4 --memory 8192` . Our recommendations are to provide at least 4 cpus for the entire deployment. 
3. Update helm to contain airflow repo: `helm repo add apache-airflow https://airflow.apache.org`
4. **In a separate terminal window run: ``minikube mount ./dags:/data/dags``**. This will create a mount point on minikube that points to the dags folder in this directory. Any file added in the dags folder will be available to containers that have this mount point. This step is required for [setting airflow on the minikube cluster](#setting-metaflow-and-airflow-with-minikube)

## Setup Metaflow and Airflow in Minikube Cluster

- Deploy Airflow using the Helm chart configuration provided in `airflow-minikube-config.yml`. The configuration values attach a volume to the dags folder for the airflow containers. Currently, the `dags` folder in the root of this repository is attached as a common volume so any new files added to this folder will create new be present inside the airflow- containers.
    
    ```bash
    helm upgrade --install airflow apache-airflow/airflow \
        -f airflow-minikube-config.yml \
        --timeout 10m0s \
        --namespace airflow --create-namespace
    ```
    
- Clone the metaflow tools repository : `git clone git@github.com:outerbounds/metaflow-tools.git`
- Deploy the helm chart for metaflow from the metaflow-tools repo. The namespace of the below deployment is `metaflow`
    
    ```bash
    helm upgrade --install metaflow metaflow-tools/k8s/helm/metaflow \
    	--timeout 15m0s \
    	--namespace metaflow \
    	--create-namespace
    ```
    

## Setting Up Auth and Metaflow Configurations

### Authentication Setup

Run the following command to extract the `AWS`-related environment variables and store them as a Kubernetes Secret in the `airflow` namespace. The below command will create a secret named `afsecret`

```bash
python metaflow_configure.py setup-aws-secrets afsecret airflow
```

### Metaflow Configuration Setup

Create `~/.metaflowconfig` folder If it doesn’t exist and then run the following command to extract a metaflow configuration for the minikube cluster and store it in the `~/.metaflow_config` folder. The command requires and S3 bucket path. 

```bash
python metaflow_configure.py export-metaflow-config <BUCKET-PATH> > ~/.metaflowconfig/config.json
```

### Creating a Test Airflow Dag from a Metaflow flow
1. Install the metaflow (With airflow support) (TODO:)

2. Since we have [added the AWS related environment variables](#authentication-setup) to `afsecret` we can just run the below command to create the `firstdag.py`  :

```bash
python flows/card_flow.py --with kubernetes:secrets='["afsecret"]' ai
rflow create dags/firstdag.py
```

### Getting Access to Airflow UI

```bash
kubectl port-forward svc/airflow-webserver 8080:8080 --namespace airflow
```

### Getting Access to Metaflow UI

```bash
kubectl port-forward svc/metaflow-metaflow-ui 8083:8083 --namespace metaflow
```