from metaflow import FlowSpec, step, card, schedule
from metaflow import airflow_external_task_sensor


@airflow_external_task_sensor(name="x", external_dag_id="S3SensorFlow", mode="poke")
@airflow_external_task_sensor(name="y", external_dag_id="SQLSensoFlow", mode="poke")
@schedule(cron="* * * * *")
class CardFlowX(FlowSpec):
    @card(type="default", id="b")
    @step
    def start(self):
        from metaflow import current

        print("current pathspec", current.pathspec)
        self.x = 1
        self.next(self.b, self.c)

    @card(type="default", id="b")
    @step
    def c(self):
        self.x += 1
        self.next(self.join)

    @card(type="default", id="b")
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
        self.x = 1
        print("Value of X is ", self.x)


if __name__ == "__main__":
    CardFlowX()
