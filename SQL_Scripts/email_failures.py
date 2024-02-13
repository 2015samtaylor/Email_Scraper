#Inserting Faulty Emails
import pandas as pd
from sshtunnel import SSHTunnelForwarder
import pymysql
from pymysql import Error
from config import ssh_username, ssh_host, ssh_password, ssh_port, mysql_database, mysql_host, mysql_password, mysql_port, mysql_username
from datetime import datetime
import logging


def find_bad_emails(outbox, failures, subject_line):
        
        try:
            #This merge occurs in order to link the message_id on the failures, ultimately finding the emailaddress
            failures = failures[['message_id', 'references']]
            failures = failures.rename(columns = {'message_id': 'message_id_failed', 'references': 'references_failed'})

            #When outbox is empty here, failures is still present

            failures = pd.merge(outbox, failures, left_on='message_id', right_on='references_failed')   #merge the reference id on the initial outbound message
          
            failures = failures.rename(columns = {'to': 'emailaddress'})

            #Maybe write directly to the customer table
            failures = failures[['emailaddress']].drop_duplicates().reset_index(drop = True)
    
            # Get current date and time
            current_datetime = datetime.now()
            formatted_date = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            failures['created_at'] = formatted_date
            # Convert the 'created_at' column to datetime format if it's not already
            failures['created_at'] = pd.to_datetime(failures['created_at'])
    
            print(f'Updating bad emails table with {len(failures)} emails - subject line {subject_line}')
            logging.info(f'Updating bad emails table with {len(failures)} emails - subject line {subject_line}')
            return(failures)
        
        except:
            print(f'No bad emails to upate with {subject_line}')
            failures = pd.DataFrame()
            return(failures)


        



def update_bad_emails(df):
    # Establish SSH tunnel
    with SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_username,
        ssh_password=ssh_password,
        remote_bind_address=(mysql_host, mysql_port),
    ) as tunnel:
        print(f'Tunnel local bind port: {tunnel.local_bind_port}')
        print(f'Tunnel is active: {tunnel.is_active}')

        # Connect to MySQL through the tunnel
        conn = pymysql.connect(
            host=mysql_host,
            port=tunnel.local_bind_port,
            user=mysql_username,
            password=mysql_password,
            database='opencartdb',
            connect_timeout=30,  # Increase the connection timeout
        )

        try:

            # Write the DataFrame to MySQL without checking for table existence
            with conn.cursor() as cursor:
                for index, row in df.iterrows():
                    try:
                        cursor.execute(f"INSERT INTO unsubscribed_email (emailaddress, created_at) VALUES (%s, %s)", (row['emailaddress'], row['created_at']))
                    except Error as e:
                        if e.args[0] == 1062:
                            print(f"Email {row['emailaddress']} already exists")
                        else:
                            print(f'First except block An error occured: {e}')

            # Commit the changes
            conn.commit()
            print('All new emails sent updated succesfully')
        
        except Exception as e:
            print(f'Second except block An error occured: {e}')
            print(type(e)) 

        finally:
            conn.close()

