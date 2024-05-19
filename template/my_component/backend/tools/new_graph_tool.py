from streamlit_ai_assist.backend.tools.base import ToolInterface
from streamlit_ai_assist.backend.data.database_connection import DatabaseConnection
from streamlit_ai_assist.backend.agents.function_rewrite_agent import FunctionRewriteAgent
from streamlit_ai_assist.backend.agents.llm import ChatLLM

import re

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def format_function(messy_string):
    clean_str = FunctionRewriteAgent(llm=ChatLLM()).rewrite_function(messy_string)
    function_name = re.search(r'def\s+(\w+\(conn\))', clean_str, re.DOTALL)
    if function_name:
        function_name = function_name.group(1)
        return [clean_str, function_name]
    else:
        function_name = re.search(r'def\s+(\w+\(conn\))', messy_string, re.DOTALL)
        if function_name:
            function_name = function_name.group(1)
            return [messy_string, function_name]
    raise Exception("Graph was not properly formatted")


class NewGraphTool(ToolInterface):

    name: str = "new_graph_tool"
    docs: list[str] = []

    def get_description(self, db) -> str:
        description = """Executes the input Python code, returning `fig`, a figure with
relevant information. The input to this action MUST be Python code and MUST follow
the following specifications:
###
The code is a Python function with the following requirements.
inputs: `conn`: a database connection. In the body of the code, data is retrieved as a pandas
dataframe using pd.read_sql(<sql>, conn) for some sql statement.
return: `fig`: an instance of plotly.graph_objs.Figure. The function MUST end with `return fig`.
###
"""
        return description

    def test_code(self, input_text: str, db):
        cleaned_code = ""
        try:
            conn = db.connect()
            cleaned_code, function_call = format_function(input_text)
            exec(cleaned_code)
            eval(function_call)
            return 'OK', cleaned_code, function_call
        except Exception as e:
            return str(e) + str(cleaned_code), None, None

    def use(self, input_text: str, db: DatabaseConnection):
        status, cleaned_code, function_call = self.test_code(input_text, db)
        if status == "OK":
            return dict(observation="Returned the new figure", tool=self.name,
                        exec=cleaned_code, eval=function_call)
        else:
            return dict(observation=f"An error was encountered in Python: {status}",
                        tool=self.name)
