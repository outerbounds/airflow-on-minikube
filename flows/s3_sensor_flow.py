import os
from metaflow import FlowSpec, step, card
from metaflow import airflow_s3_key_sensor, airflow_schedule_interval

# Run this file with `SENSOR_PATH` environment variable set to the absolute S3 Path

SENSOR_PATH = os.environ.get("SENSOR_PATH", "")


@airflow_schedule_interval(cron="* * * * *")
@airflow_s3_key_sensor(bucket_key=SENSOR_PATH, mode="poke")
class S3SensorFlow(FlowSpec):
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
    S3SensorFlow()
