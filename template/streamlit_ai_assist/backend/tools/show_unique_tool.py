import re

import pandas as pd

from streamlit_ai_assist.backend.tools.base import ToolInterface


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
        return "OK", df, dataframe_to_text_table(df)
    except Exception as e:
        return "ERROR", None, f'Failed with error: {str(e)}. Choose another Action.'


class ShowUniqueTool(ToolInterface):

    name: str = "show_unique_tool"
    docs: list[str] = []

    def get_description(self, db) -> str:
        return """Given a table name and a column, returns which unique values exist
 in the column of the table.
 Useful for showing which values of a categorical value exist so that filters
 can be created down the line.
 Input to this tool
 MUST use the format (<table name>, <column name>). E.g. (zoo, species)
"""

    def use(self, input_text: str, db):
        match = re.findall(r'\((\w+),\s*(\w+)\)', input_text)
        if match:
            match = match[0]
        else:
            return dict(
                observation="Sorry your input is in an incorrect format. Please try again with format (<table name>, <column name>) ",
                tool=self.name,
            )
        table_name = match[0]
        column_name = match[1]
        query = f"SELECT DISTINCT {column_name} FROM {table_name} LIMIT 50"
        status, table_df, table_text = query_to_dataframe(query, db)
        if status == "OK":
            return dict(
                observation=table_text,
                tool=self.name,
                print=table_text,
            )
        else:
            return dict(observation=table_text, tool=self.name)
