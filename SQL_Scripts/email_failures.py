#Inserting Faulty Emails
import pandas as pd
from sshtunnel import SSHTunnelForwarder
import pymysql
from pymysql import Error
from config import ssh_username, ssh_host, ssh_password, ssh_port, mysql_database, mysql_host, mysql_password, mysql_port, mysql_username
from datetime import datetime


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
                            print(f'An error occured: {e}')

            # Commit the changes
            conn.commit()
            print('All new emails sent updated succesfully')
        
        except Exception as e:
            print('An error occured: {e}')

        finally:
            conn.close()

