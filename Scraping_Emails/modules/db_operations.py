import pyodbc
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import urllib

class DatabaseConnector:

    def __init__(self, server, database, username, password, sql_db, sql_table):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}'
        self.conn = pyodbc.connect(self.conn_str)
        self.sql_db = sql_db
        self.sql_table = sql_table

    def SQL_query(self, query):
        df_SQL = pd.read_sql_query(query, con=self.conn)
        return(df_SQL)

    def generate_sql_engine(self):
        quoted = urllib.parse.quote_plus(self.conn_str)
        engine = sqlalchemy.create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))
        return(engine)

    def get_dtypes(self, db, table_name):

        out = self.SQL_query('''
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH 
        FROM {}.information_schema.columns
        WHERE table_name = '{}'
        '''.format(self.sql_db, self.sql_table))

        dtypes = {}
        
        #gets column name, data type, char length into a dict
        for _, row in out.iterrows():
            column_name = row['COLUMN_NAME']
            data_type = row['DATA_TYPE']
            length = row['CHARACTER_MAXIMUM_LENGTH']
            if data_type == 'varchar' or data_type == 'nvarchar':
                dtypes[column_name] = sqlalchemy.types.VARCHAR(length=int(length))
            elif data_type == 'int':
                dtypes[column_name] = sqlalchemy.types.Integer()
            elif data_type == 'float':
                dtypes[column_name] = sqlalchemy.types.Float()
            elif data_type == 'datetime':
                dtypes[column_name] = sqlalchemy.types.DateTime()
            elif data_type == 'text':
                dtypes[column_name] = sqlalchemy.types.Text()
            elif data_type == 'char':
                dtypes[column_name] = sqlalchemy.types.VARCHAR(length=int(length))

        return(dtypes)

    def send(self, frame):
        engine = self.generate_sql_engine()
        dtypes = self.get_dtypes(self.sql_db, self.sql_table)

        # Create or replace the table with the correct data types
        frame.to_sql(self.sql_table, con=engine, index=False, dtype=dtypes, if_exists='append')









