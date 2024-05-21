from streamlit.connections import SnowflakeConnection
import streamlit as st


class DatabaseConnection():

    def __init__(self, name: str):
        self.name = name
        self.conn = st.connection(self.name)
        if isinstance(self.conn, SnowflakeConnection):
            self.raw_connection = self.conn.raw_connection
            self.dialect = "snowflake"
        else:
            self.raw_connection = self.conn.engine.raw_connection()
            self.dialect = self.conn.engine.dialect.name

    def get_dialect(self):
        return self.dialect

    def query(self, sql):
        return self.conn.query(sql)

    def connect(self):
        return self.raw_connection
