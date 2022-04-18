from metaflow import FlowSpec, step, card, Parameter, JSONType

class CardFlow(FlowSpec):

    param_a = Parameter("some-rogue-param", default=1)

    param_b = Parameter("some-2", default="safasdf", type=str)

    param_d = Parameter(
        "json-param", help="Country-GDP Mapping", type=JSONType, default='{"US": 1939}'
    )

    param_e = Parameter(
        "boolean-param", help="Country-GDP Mapping", type=bool, default=False
    )

    @card(type="default", id="b")
    @step
    def start(self):
        from metaflow import current
        print("current pathspec", current.pathspec)
        self.x = 1
        print("Value of param_a", self.param_a)
        print("Value of json param : ", self.param_d["US"])
        print("Type of boolean param : ", type(self.param_e), self.param_e)
        self.next(self.b)

    def _fake_series(self, n, g):
        import random
        import math

        return [(random.random() - 0.5) * 0.1 + math.sin(x * g) for x in range(n)]

    @card(type="default", id="b")
    @step
    def b(self):
        self.x += 1
        self.next(self.end)

    @card(type="default", id="b")
    @step
    def end(self):
        self.x += 1
        print("Value of X is ", self.x)


if __name__ == "__main__":
    CardFlow()
