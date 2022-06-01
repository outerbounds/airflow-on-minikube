from metaflow import FlowSpec, step, card, Parameter
from metaflow import airflow_sql_sensor, airflow_schedule_interval, project

CONNECTION_STR = "k8s-airflow-postgres"


@airflow_schedule_interval
@airflow_sql_sensor(
    sql="select count(*) from company;", mode="poke", conn_id=CONNECTION_STR
)
class SQLSensoFlow(FlowSpec):
    @card(type="default", id="b")
    @step
    def start(self):
        self.x = 1
        self.next(self.b, self.c)

    @step
    def c(self):
        self.x += 1
        self.next(self.join)

    @step
    def b(self):
        self.x += 1
        self.next(self.join)

    @step
    def join(self, inputs):
        self.x = max(inputs.c.x, inputs.b.x)
        self.next(self.end)

    @card(type="default", id="b")
    @step
    def end(self):
        self.x += 1
        print("Value of X is ", self.x)


if __name__ == "__main__":
    SQLSensoFlow()
