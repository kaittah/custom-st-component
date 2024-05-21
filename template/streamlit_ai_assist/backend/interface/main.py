import importlib
import streamlit as st

from streamlit_ai_assist.backend.agents.data_analyst_agent import DataAnalystAgent
from streamlit_ai_assist.backend.agents.conversational_agent import ConversationalAgent
from streamlit_ai_assist.backend.agents.llm import ChatLLM
from streamlit_ai_assist.backend.tools import (
    ShowTablesTool,
    SchemaTool,
    ShowUniqueTool,
    SQLTool,
    GraphTool,
    NewGraphTool
)
from streamlit_ai_assist.backend.documents import python_to_docs
from streamlit_ai_assist.backend.data.database_connection import DatabaseConnection
from streamlit_ai_assist.backend.interface.renderable import Renderable, RenderType

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio



@st.cache_resource
def get_database(database_name):
    return DatabaseConnection(name=database_name)


@st.cache_resource
def load_agents(database_name, general_description, docs):
    db = get_database(database_name)
    data_analyst = DataAnalystAgent(
                llm=ChatLLM(),
                tools=[
                    ShowTablesTool(),
                    SchemaTool(),
                    ShowUniqueTool(),
                    SQLTool(),
                    GraphTool(docs=docs),
                    NewGraphTool()
                ],
                db=db
            )
    conversational_agent = ConversationalAgent(
            llm=ChatLLM(),
            general_description=general_description,
            data_analyst=data_analyst
        )
    return data_analyst, conversational_agent


class DataAnalystChat:

    def __init__(
            self,
            graphing_file_path,
            graphing_import_path,
            database_name,
            general_description
    ):
        self.graphing_file_path: str = graphing_file_path
        self.graphing_import_path: str = graphing_import_path
        self.database_name: str = database_name
        self.general_description: str = general_description

    def run(self, prompt):
        if not prompt or prompt == "None" or prompt is None:
            return []

        to_render = []

        docs = python_to_docs(self.graphing_file_path)
        data_analyst, conversational_agent = load_agents(
            self.database_name,
            self.general_description,
            docs
        )
        conversational_agent.clear_data()
        data_analyst.clear_data()
        db = get_database(self.database_name)

        next_message, results_list = conversational_agent.run(prompt)

        for row in results_list:

            if row["eval"] and row["tool"] == "graph_tool":
                conn = db.connect()
                imported_graphing_library = importlib.import_module(self.graphing_import_path)
                func = eval(f'imported_graphing_library.{row["eval"]}')
                fig = func(conn)
                to_render.append(Renderable(type=RenderType.GRAPH, content=pio.to_json(fig)))

            elif row["eval"] and row["exec"] and row["tool"] == "new_graph_tool":
                conn = db.connect()
                exec(row["exec"])
                fig = eval(row["eval"])
                to_render.append(Renderable(type=RenderType.NEW_GRAPH, content=pio.to_json(fig),
                                            code=row["exec"], function_name=row["eval"]))

            elif row["print"]:
                to_render.append(Renderable(type=RenderType.TABLE, content=row["print"]))

        to_render.append(Renderable(type=RenderType.RESPONSE_BOX, content=next_message))
        return to_render
