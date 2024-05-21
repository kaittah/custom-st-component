# streamlit-ai-assist

`streamlit-ai-assist` uses the power of [Snowflake Arctic](https://www.snowflake.com/blog/arctic-open-efficient-foundation-language-models-snowflake/), an open_source LLM, to personalize dashboards and allow all audiences to easily explore new and pre-built data visualizations. It's a built-in data analyst for your Streamlit dashboard.

If you add this component to your dashboard, dashboard viewers will be able to chat with an LLM assistant to get answers to their questions. If there are relevant graphs already in the dashboard, then the assistant will display those. If the question requires a new graph, the LLM is able to write the code to create that. These **new graphs** are highlighted in yellow, and if GitHub connection is configured in the app, then the user will be allowed to easily create a **PR** that integrates the code into the dashboard once reviewed and approved by a team member.

If a user has a particular question, the AI assistant can execute SQL `SELECT` statements that let it access the raw numbers. It can summarize graphs for you and return answers to a quick question you have.

The bottom view of the streamlit component is a preview of the most relevant graphs already in the dashboard that relate to the user input. You can therefore quickly search and filter different visuals if you haven't formulated any questions yet.



## Installation instructions

```sh
pip install streamlit-custom-component
```

## Usage instructions

```python
import streamlit as st

from streamlit_ai_assist import streamlit_ai_assit

streamlit_ai_assist(
            graphing_file_path="graphing.py",
            graphing_import_path="graphing",
            database_name="snowflake",
            general_description="This is a database for a company that does X",
            key="foo1"
)

```