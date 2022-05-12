# User API Documentation

The following are the key user-related constructs exposed by metaflow to support the Airflow universe:

1. A CLI command to create airflow workflow DAG file from metaflow `FlowSpec`. 
2. Programmic API changes : Flow level decorator support for:
    1. `schedule_interval` specification. `schedule_interval` determines how often a dag is scheduled on Airflow. 
    2. Airflow offers a "task-level construct" named [Sensors](https://airflow.apache.org/docs/apache-airflow/2.3.0/concepts/sensors.html). Sensors essentially wait for some event to take place based on the sensor's usecase. Metaflow's Airflow integration supports usage of sensors at a flow level.


## How it works

Metaflow users can now easily compile Metaflow workflows into airflow compatible workflows. Every Metaflow `FlowSpec` file exposes a `airflow create` command to compile the workflow into an Airflow DAG file. Under the hood metaflow packages the code packages, stores them in S3 and then compiles the code into a airflow compatible python file. The generated file can be moved to the Airflow scheduler's DAGs folder. From there the scheduler will run the workflow as a native airflow workflow. 

Metaflow requires Kubernetes as Airflow's compute-execution medium. Metaflow leverages the Airflow `KuberneterPodOperator` to run different `@step`s on Kubernetes via Airflow. Airflow sensors can be also attached to the start of a flow using airflow sensor related flow decorators. Users can attach many sensor related decorators to a flow and the flow will wait for all sensors to succeed before starting. Each sensor decorator also takes a `soft_fail` argument that can allow a sensor to fail and still trigger the Metaflow dag. Every sensor decorator accepts parameters of [BaseOperator](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/sensors/base/index.html#airflow.sensors.base.BaseSensorOperator) class in Airflow. Every sensor related decorator will also add system tags. 

## CLI Usage
Metaflow exposes an `airflow create` command from the FlowSpec file's cli. This command can help convert a FlowSpec file into a Airflow DAG.  
```
Usage: python myflow.py airflow create [OPTIONS] FILE_PATH

  Create an airflow workflow from this metaflow workflow

Options:
  --tag TEXT                 Annotate the DAG on Airflow and any of it's
                             metaflow runs with the given tag. You can specify
                             this option multiple times to attach multiple
                             tags.

  --name TEXT                `dag_id` of airflow DAG. The flow name is used
                             instead if this option is not specified

  --is-paused-upon-creation  Sets `is_paused_upon_creation=True` for the
                             Airflow DAG.

  --namespace TEXT
  --max-workers INTEGER      Maximum number of concurrent Airflow tasks.
                             [default: 100]

  --worker-pool TEXT         Worker pool the for the airflow tasks.
  --help                     Show this message and exit.
```



## Airflow Sensor Related Decorator Usage
Metaflow exposes the following Airflow sensor related flow-decorators: 
- `@airflow_s3_key_sensor`
- `@airflow_sql_sensor`
- `@airflow_external_task_sensor`

Each decorator will take the following common arguments: 
- `timeout` [default: 3600]:  Timeout after which the sensor is considered "failed"
- `poke_interval` [default: 60]:  Interval the sensor keeps poking
- `mode` : [default: "reschedule"], :  be `poke` or `reschedule`
- `exponential_backoff` [default: True]:  Will exponentially increase the time it takes to for the next "poke"
- `pool` [default: None]:  Airflow Worker pool. 
- `soft_fail` [default: False]:  If the sensor fails it will still trigger the downstream task
- `name` [default: None]:  `task_id` for the sensor on Airflow
- `description` [default: None]:  Description for the sensor task on Airflow.

### External Task Sensors

Example : [flows/external_task_sensor.py](./flows/external_task_sensor.py)
```python
@airflow_external_task_sensor(
    ### ------------------ External TaskSensor Args -------------
    external_dag_id=None, # `dag_id` of the upstream Airflow DAG
    external_task_ids=None, # `task_id` of the upstream Airflow DAG
    allowed_states=["success"], # Allowed state of the upstream DAG. ie. Trigger only if dag status is "success" or "failure" or "queued" etc. 
    failed_states=None, # A list of failed or dis-allowed states 
    execution_delta=None, #  time difference with the previous execution to look at, the default is the same logical date as the current task or DAG. Needs to be `datetime.timedelta`
    check_existence=True, #  Set to True to check if the external task exists (when external_task_id is not None) or check if the DAG to wait for exists (when external_task_id is None), and immediately cease waiting if the external task or DAG does not exist (default value: False).
    ### ------------------ ------------------ ------------------
)
class MyFlow(FlowSpec):
    ...
    ...
```

### SqlSensor

Example : [flows/sql_sensor_flow.py](./flows/sql_sensor_flow.py)
```python
@airflow_sql_sensor(
    ### ------------------ SqlSensor Args -------------
    conn_id=None, # Connection id of the SQL connection set via the Airflow UI
    sql=None, # SQL statement to poke and validate
    fail_on_empty=True, # Explicitly fail on no rows returned
    parameters=None #  The parameters to render the SQL query with (optional).
    ### ------------------ ------------------ ------------------
)
class MyFlow(FlowSpec):
    ...
    ...
```

### S3Sensor

Example : [flows/s3_sensor_flow.py](./flows/s3_sensor_flow.py)
```python
@airflow_s3_key_sensor(
    ### ------------------ S3KeySensor Args -------------
    bucket_key=None,  # Required
    bucket_name=None, # If bucket key doesn't start with s3://
    wildcard_match=False, # Matches wildcards with "*"
    aws_conn_id=None, # Connection Id for AWS set via the Airflow UI
    verify=None,  # `verify (Optional[Union[str, bool]])` Whether or not to verify SSL certificates for S3 connection.
    ### ------------------ ------------------ ------------------
)
class MyFlow(FlowSpec):
    ...
    ...
```

## Scheduling Airflow Dags
Metaflow exposes a `@airflow_schedule_interval` decorator to configure the scheduling of airflow dags. `@airflow_schedule_interval` takes the same arguments are [@schedule](http://docs.metaflow.org/going-to-production-with-metaflow/scheduling-metaflow-flows/scheduling-with-argo-workflows#scheduling-a-flow). Attaching this decorator to a flow also adds a `--schedule` option to the CLI :  

```sh
python myflow.py --schedule '* * * * *' airflow create minutelydag.py
```

You can even use airflow presets with the `--schedule` option for configuring the scheduling/cron interval
```sh
python myflow.py --schedule @daily airflow create minutelydag.py
```
# Resources 
1. [Airflow Task Instance](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/taskinstance/index.html#airflow.models.taskinstance.TaskInstance)
2. [Airflow Task Object](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/taskmixin/index.html)
3. [Airflow Dag Run](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/dagrun/index.html#airflow.models.dagrun.DagRun)