import pyodbc
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import update
import urllib
import logging



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



    def update_column(self, engine, frame, update_column):
        # Create a reference to the SQLAlchemy table object
        metadata = sqlalchemy.MetaData(bind=engine)
        table = sqlalchemy.Table(self.sql_table, metadata, autoload=True)

        # Use SQLAlchemy to create a connection and a transaction
        with engine.connect() as connection, connection.begin():
            # Iterate through the DataFrame rows
            for _, row in frame.iterrows():
                # Build an update query
                update_stmt = (
                    update(table)
                    .where(table.c['message_id'] == row['message_id'])
                    .values({update_column: row[update_column]})
                )

                # Execute the update statement
                connection.execute(update_stmt)



    def send(self, frame, table_name, update_column=None):
        engine = self.generate_sql_engine()
        dtypes = self.get_dtypes(self.sql_db, self.sql_table)

        #This is present in order to update the reply_thread updates in thread table
        if update_column:
            # Update only the specified column
            self.update_column(engine, frame, update_column)
            
        else:

            distinct_ids = self.SQL_query(f'SELECT DISTINCT message_id FROM [emailcampaign].[dbo].[{table_name}]')

            if distinct_ids.empty:
                logging.info(f'{table_name} is empty sending over all rows')
                print(f'{table_name} is empty sending over all rows')
                frame.to_sql(self.sql_table, con=engine, index=False, dtype=dtypes, if_exists='append')

            else:

                #If rows exist in the DB, check to see what isnew
                new_rows = pd.merge(frame, distinct_ids, on = 'message_id', indicator=True)
                new_rows = new_rows.loc[new_rows['_merge'] == 'left_only']

                if not new_rows.empty:
                    logging.info(f'{len(new_rows)} new emails appended to email_history')
                    print(f'{len(new_rows)} new emails appended to email_history')
                    new_rows.to_sql(self.sql_table, con=engine, index=False, dtype=dtypes, if_exists='append')
                else:
                    logging.info('No new sent emails to append to email_history')
                    print('No new sent emails to append to email_history')
            
                
    
    def update_reply_thread(self, thread):

        # Retrieve existing recipient_ids from the 'thread' table
        existing_ids_thread = self.SQL_query(f'SELECT DISTINCT message_id FROM {self.sql_db}.dbo.{self.sql_table}')

        # Merge the 'thread' table with the provided 'thread' DataFrame
        pre_existing_thread_updates = pd.merge(thread, existing_ids_thread, on='message_id')

        # Filter rows where 'reply_thread' is not empty
        pre_existing_thread_updates = pre_existing_thread_updates[pre_existing_thread_updates['reply_thread'] != '']

   

        # Check if there are pre-existing threads to update, and if they are not empty
        if pre_existing_thread_updates.empty == True:
            print('No pre-existing threads to update')
            logging.info('No pre-existing threads to update')
        else:
            print(f'{len(pre_existing_thread_updates)} threads have been updated')
            logging.info(f'{len(pre_existing_thread_updates)} threads have been updated')
            # Use the send method to update the 'reply_thread' column
            self.send(pre_existing_thread_updates, 'thread', update_column='reply_thread')









