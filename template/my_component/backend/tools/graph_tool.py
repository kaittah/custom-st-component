from my_component.backend.tools.base import ToolInterface
from my_component.backend.data.database_connection import DatabaseConnection


class GraphTool(ToolInterface):

    name: str = "graph_tool"
    docs: list[str] = []

    def get_description(self, db) -> str:
        description = """Given a function name,
executes the below function with that name and displays the figure to the end customer.
Using the functions below, you can infer names of tables in the database and relationships you
can use to write a SQL query or new graphs that you will plot in actions.
If using the graph_tool in this step, in the next steps, you must
get a summary of the data in the graph using SQL.
The input MUST BE exactly one name of the available functions:
```
"""
        for s in self.docs:
            description = description + s
        return description + "```"

    def check_function_name(self, input_text) -> bool:
        for doc in self.docs:
            if f"def {input_text}(" in doc:
                return True
        return False

    def use(self, input_text: str, db: DatabaseConnection):
        function_name = input_text.strip().split('(')[0]
        if self.check_function_name(function_name):
            return dict(observation=f"Displayed graph with function name {input_text}",
                        eval=function_name, tool=self.name)

        else:
            return dict(observation=f"The function with name {input_text} does not exist",
                        tool=self.name)
