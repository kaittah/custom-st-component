import pandas as pd

from my_component.backend.tools.base import ToolInterface


def dataframe_to_text_table(df: pd.DataFrame) -> str:
    table_str = df.to_string(index=False)
    rows = table_str.split('\n')
    headers = rows[0]
    header_line = '-'*len(headers)
    formatted_table = [headers, header_line] + rows[1:]
    formatted_table_str = '\n'.join(formatted_table)
    return formatted_table_str


def query_to_dataframe(query, db):
    try:
        df = db.query(query)
        n_rows = df.shape[0]
        n_cols = df.shape[1]
        if n_rows < 100 and n_cols < 5:
            return "OK", df, dataframe_to_text_table(df)
        else:
            return "ERROR", None,  f"""The resulting table is too large.
 The dimensions are {n_rows} rows by {n_cols} cols. There can be at most 100 rows and 5 columns.
 This tool can only be used to summarize data. Choose another action.
"""
    except Exception as e:
        return "ERROR", None, f'The SQL query failed with error: {str(e)}. Choose another Action.'


class SQLTool(ToolInterface):
    name: str = "sql_tool"
    docs: list[str] = []

    def get_description(self, db) -> str:
        dialect = db.get_dialect()
        return f"""Executes the given sql query against a given database with dialect {dialect}
 and returns a table of results.
 You must ONLY use this with queries with GROUP BY clauses in order to answer
 a question or describe a graph.
"""

    def use(self, input_text: str, db):
        status, table_df, table_text = query_to_dataframe(input_text, db)
        if status == "OK":
            return dict(observation=table_text, tool=self.name, print=table_text)
        else:
            return dict(observation=table_text, tool=self.name)
