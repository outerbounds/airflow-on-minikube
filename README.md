# How to Run Metaflow with Airflow on Minikube


# Setting Metaflow and Airflow with Minikube

Since the current version of Airflow support in metaflow requires S3 access. Please configure a S3 bucket and ensure you have AWS credentials in your environment variables. In order to run metaflow flows with airflow on minikube the following is required: 

1. [Setup, helm, minikube, and a dag folder mount point to the minikube cluster](#setup-helm-and-minikube)
2. [Set Kubernetes Namespaces and AWS related Kubernetes Secrets.](#authentication)
3. [Setup Metaflow and airflow on the minikube cluster](#setup-metaflow-and-airflow-in-minikube-cluster)
4. [Setup metaflow related configurations](#setting-up-auth-and-metaflow-configurations)
    1. [Setup Kubernetes related secrets for AWS](#authentication-setup)
    2. [Setup metaflow related configuration](#metaflow-configuration-setup)
    3. [Run a test flow after setting up above configuration](#creating-a-test-airflow-dag-from-a-metaflow-flow)
    4. Access the [Airflow](#getting-access-to-airflow-ui) and [Metaflow UI](#getting-access-to-metaflow-ui)
    5. TODO: Access the results of your flow programmatically

## Setup Helm and Minikube

1. `brew install minikube helm`. We recommend helm version >= 2.5.0.
2. Start minikube with a certain number of resources:`minikube start --cpus 4 --memory 8192` . Our recommendations are to provide at least 4 cpus for the entire deployment. 
3. Update helm to contain airflow repo: `helm repo add apache-airflow https://airflow.apache.org`
4. **In a separate terminal window run: ``minikube mount ./dags:/data/dags``**. This will create a mount point on minikube that points to the dags folder in this directory. Any file added in the dags folder will be available to containers that have this mount point. This step is required for [setting airflow on the minikube cluster](#setup-metaflow-and-airflow-in-minikube-cluster). You can change `./dags` to any directory where you will host Airflow DAGs. 

## Namespace and Authentication Setup
1. Install the `requirements` file with `pip`. 
```bash
pip install -r requirements.txt # install the requirements file. 
```
2. Create a namespace for `metaflow` and `airflow` deployment
```bash
kubectl create namespace metaflow
kubectl create namespace airflow
```
3. Once the namespaces have been created, we will setup AWS related credentials in the metaflow and airflow namespaces. The below command extracts the environment variables in your local shell starting with `AWS` and creates secrets with those environment variables in the `airflow` and `metaflow` namespaces. These secrets will be essential to run the metaflow related via airflow. 
```
python metaflow_configure.py setup-aws-secrets afsecret airflow
python metaflow_configure.py setup-aws-secrets afsecret metaflow
```

## Setup Metaflow and Airflow in Minikube Cluster

- Deploy Airflow using the Helm chart configuration provided in `airflow-minikube-config.yml`. The configuration values attach a volume to the dags folder for the airflow containers. Currently, the `dags` folder in the root of this repository is attached as a common volume so any new files added to this folder will create new be present inside the airflow-containers.
    
    ```bash
    helm upgrade --install airflow apache-airflow/airflow \
        -f airflow-minikube-config.yml \
        --timeout 10m0s \
        --namespace airflow --create-namespace
    ```
- Install and `nginx-ingress` in the minikube cluster : `minikube addons enable ingress`
- Clone the metaflow tools repository : `git clone git@github.com:outerbounds/metaflow-tools.git`
- Deploy the helm chart for metaflow from the metaflow-tools repo. The namespace of the below deployment is `metaflow`. Change the path for `s3://mybucket` to the path of the bucket. Change `metaflow-ui.envFrom[0].secretRef.name` **only if you have set a different secret name**. 
    
    ```bash
    helm upgrade --install metaflow metaflow-tools/k8s/helm/metaflow \
    	--timeout 15m0s \
    	--namespace metaflow \
    	--create-namespace \
        --set metaflow-ui.METAFLOW_DATASTORE_SYSROOT_S3=s3://mybucket/metaflow \
        --set "metaflow-ui.envFrom[0].secretRef.name=afsecret" \
        --set metaflow-ui.ingress.className=nginx \
        --set metaflow-ui.ingress.enabled=true
    ```
    

## Metaflow Configurations

### Metaflow Configuration Setup

Create `~/.metaflowconfig` folder If it doesn’t exist and then run the following command to extract a metaflow configuration for the minikube cluster and store it in the `~/.metaflow_config` folder. The command requires and S3 bucket path. 

```bash
python metaflow_configure.py export-metaflow-config s3://mybucket > ~/.metaflowconfig/config.json
```

### Creating a Test Airflow Dag from a Metaflow flow
1. Install the metaflow (With airflow support) (TODO:)

2. Since we have [added the AWS related environment variables](#authentication-setup) to `afsecret` we can just run the below command to create the `firstdag.py`  :

```bash
python flows/card_flow.py --with kubernetes:secrets='["afsecret"]' airflow create dags/firstdag.py
```

### Getting Access to Airflow UI
Run the below command to port forward the UI from the minikube cluster. After running the command you can access the UI at `http://localhost:8080`
```bash
kubectl port-forward svc/airflow-webserver 8080:8080 --namespace airflow
```

### Getting Access to Metaflow UI
TODO