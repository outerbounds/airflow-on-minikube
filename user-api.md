# User API Documentation

The following are the key user-related constructs exposed by metaflow to support the Airflow universe:

- A CLI command to create airflow workflow DAG file from metaflow `FlowSpec`. 

## How it works

Metaflow users can now easily compile Metaflow workflows into airflow compatible workflows. Every Metaflow `FlowSpec` file exposes a `airflow create` command to compile the workflow into an Airflow DAG file. Under the hood metaflow packages the code packages, stores them in S3 and then compiles the code into a airflow compatible python file. The generated file can be moved to the Airflow scheduler's DAGs folder. From there the scheduler will run the workflow as a native airflow workflow. 

Metaflow requires Kubernetes as Airflow's compute-execution medium. Metaflow leverages the Airflow `KuberneterPodOperator` to run different `@step`s on Kubernetes via Airflow. 

## Decorator Support 
`@conda`,`@catch`, `@retry`,`@card`,`@project`,`@environment`,`@timeout`,`@environment`,`@kubernetes`,`@resources`
## Version Support 
A minimum Airflow version of `2.2.0` is required to support basic Metaflow decorators and flows with nested branches. _*Foreach's are not supported with Airflow version 2.2.0*_. Decorators like `@batch` is are also not supported with Airflow. Airflow introduced [dynamic task mapping](https://airflow.apache.org/docs/apache-airflow/stable/concepts/dynamic-task-mapping.html) in version 2.3.0. Metaflow will very soon support foreach's which can work with Airflow version `2.3.0`. _*Foreach support will also require that the airflow installation has [apache-airflow-providers-cncf-kubernetes](https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/index.html) provider installed at minimum of version 4.2.0*_.  


## CLI Usage
Metaflow exposes an `airflow create` command from the FlowSpec file's cli. This command can help convert a FlowSpec file into a Airflow DAG.  
```
Usage: python myflow.py airflow create [OPTIONS] FILE

  Compile a new version of this flow to Airflow DAG.

Options:
  --authorize TEXT            Authorize using this production token. You need
                              this when you are re-deploying an existing flow
                              for the first time. The token is cached in
                              METAFLOW_HOME, so you only need to specify this
                              once.

  --generate-new-token        Generate a new production token for this flow.
                              This will move the production flow to a new
                              namespace.

  --new-token TEXT            Use the given production token for this flow.
                              This will move the production flow to the given
                              namespace.

  --tag TEXT                  Annotate all objects produced by Airflow DAG
                              executions with the given tag. You can specify
                              this option multiple times to attach multiple
                              tags.

  --is-paused-upon-creation   Generated Airflow DAG is paused/unpaused upon
                              creation.

  --namespace TEXT            Change the namespace from the default to the
                              given tag. See run --help for more information.

  --max-workers INTEGER       Maximum number of parallel processes.  [default:
                              100]

  --workflow-timeout INTEGER  Workflow timeout in seconds. Enforced only for
                              scheduled DAGs.

  --worker-pool TEXT          Worker pool for Airflow DAG execution.
  --help                      Show this message and exit
```

## Scheduling Airflow Dags
Metaflow compile airflow DAGs can be scheduled via [@schedule](http://docs.metaflow.org/going-to-production-with-metaflow/scheduling-metaflow-flows/scheduling-with-argo-workflows#scheduling-a-flow) decorator. 

# Resources 
1. [Airflow Task Instance](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/taskinstance/index.html#airflow.models.taskinstance.TaskInstance)
2. [Airflow Task Object](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/taskmixin/index.html)
3. [Airflow Dag Run](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/dagrun/index.html#airflow.models.dagrun.DagRun)