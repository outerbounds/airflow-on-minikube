import subprocess
import os
import click
import json

DEBUG_STUFF = int(os.environ.get("DEBUG", "0"))
_logger = None


def get_logger(name):
    global _logger
    if _logger is not None:
        return _logger
    import logging

    logging.basicConfig(
        format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p"
    )
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if DEBUG_STUFF else logging.INFO)
    _logger = logger
    return logger


def bash_command(func):
    def wrapper(*args, **kwargs):
        cmd = func(*args, **kwargs)
        if isinstance(cmd, list):
            global _logger
            try:
                opx = subprocess.check_output(
                    cmd, stderr=subprocess.PIPE, env=os.environ
                )
            except subprocess.CalledProcessError as e:
                if DEBUG_STUFF and _logger:
                    _logger.debug(e.stderr.decode("utf-8"))
                raise e
            if DEBUG_STUFF and _logger:
                _logger.debug(opx.decode("utf-8"))
            return opx
        return cmd

    return wrapper


def pretty_print_subprocess_error(func):
    def wrapper(*args, **kwargs):
        try:
            cmd = func(*args, **kwargs)
        except subprocess.CalledProcessError as e:
            click.secho(e.stderr.decode(), fg="red")
            exit()
        return cmd

    return wrapper


def as_json(func):
    def wrapper(*args, **kwargs):
        output = func(*args, **kwargs)
        return json.loads(output)

    return wrapper


@click.group()
def cli():
    pass


@pretty_print_subprocess_error
@as_json
@bash_command
def get_service(namespace,deployment_name=None):
    return [
        "kubectl",
        "get",
        "svc/%s"%deployment_name,
        "-n",
        namespace,
        '-o',
        'json'
    ]


@pretty_print_subprocess_error
@bash_command
def create_aws_secret(secret_name, namespace):
    secrets = [
        "--from-literal=%s=%s" % (k, os.environ[k]) for k in os.environ if "AWS" in k
    ]
    if len(secrets) == 0:
        return ["echo", "AWS environment variables found"]
    cmd = ["kubectl", "create", "secret", "generic", secret_name, "-n", namespace]
    cmd += secrets
    return cmd


@cli.command(
    "setup-aws-secrets",
    help="Setup current AWS environment variables as a kubernetes secret in a namespace",
)
@click.argument("secret-name")
@click.argument("namespace")
def setup_secrets(secret_name, namespace):
    click.secho(create_aws_secret(secret_name, namespace).decode(), fg="green")


@cli.command(
    "export-metaflow-config",
    help="Export the metaflow configuration from kubernetes cluster",
)
@click.argument("bucket-path")
@click.option("--airflow-namespace", "airflow_ns", default="airflow")
@click.option("--metaflow-namespace", "mf_ns", default="metaflow")
@click.option("--metaflow-helm-deployment-name", "mf_helm", default="metaflow")
def export_config(bucket_path, airflow_ns, mf_ns, mf_helm):
    click.secho(
        json.dumps(
            setup_config(
                os.path.join(bucket_path, "metaflow"),
                os.path.join(bucket_path, "data"),
                mf_ns,
                airflow_ns,
                '%s-metaflow-service'%mf_helm
            ),
            indent=4,
        ),
        fg="green",
    )


def setup_config(s3_root, datatools_root, metaflow_namespace, airflow_namespace, metaflow_deployment_name):
    service_dec = get_service(metaflow_namespace,deployment_name=metaflow_deployment_name)
    md_ports = [p for p in service_dec['spec']['ports'] if p['name']=='metadata']
    return {
        "METAFLOW_DATASTORE_SYSROOT_S3": s3_root,
        "METAFLOW_DATATOOLS_S3ROOT": datatools_root,
        "METAFLOW_DEFAULT_DATASTORE": "s3",
        "METAFLOW_DEFAULT_METADATA": "service",
        "METAFLOW_SERVICE_URL": "http://%s:%s/" % (service_dec['spec']['clusterIP'],str(md_ports[0]['port'])),
        "METAFLOW_KUBERNETES_NAMESPACE": airflow_namespace,
        # "METAFLOW_KUBERNETES_SERVICE_ACCOUNT":"metaflow-service-account",
    }


if __name__ == "__main__":
    cli()
