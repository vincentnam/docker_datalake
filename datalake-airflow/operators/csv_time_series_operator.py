from airflow.models.baseoperator import BaseOperator

class CSVTimeSeriesOperator(BaseOperator):

    def __init__(
        self,
        name: str,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.name = name 

    def execute(self, context):
        message = "Hello {}".format(self.name)
        print(message)
        return message