from my_component.backend.tools.base import ToolInterface


def get_schema(table_name, db):
    sql_driver = db.get_dialect()
    try:
        schema = f'TABLE {table_name} EXISTS WITH SCHEMA:\n'
        if sql_driver == 'snowflake':
            query = f'DESC table {table_name}'
        else:
            query = f'PRAGMA table_info({table_name})'
        conn = db.connect()
        cur = conn.cursor()
        cur.execute(query)
        results = cur.fetchall()
        for row in results:
            schema = schema + f'{row[0]} {row[1]}\n'
        return schema
    except Exception:
        return f'TABLE {table_name} DOES NOT EXIST\n'


class SchemaTool(ToolInterface):
    name: str = "schema_tool"
    docs: list[str] = []

    def get_description(self, db) -> str:
        return """Given a comma separated list of database table names,
returns the schema of those tables. The input
must be one of the formats: <table_name> OR <table_name_1>,<table_name_2>,...,<table_name_n>"""

    def use(self, input_text: str, db):
        table_names = input_text.split(',')
        result = ''
        for table_name in table_names:
            result = result + get_schema(table_name, db)
        return dict(observation=result, tool=self.name)
