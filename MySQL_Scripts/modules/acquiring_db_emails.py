import pandas as pd
from sshtunnel import SSHTunnelForwarder
import pymysql
from config import ssh_username, ssh_host, ssh_password, ssh_port, mysql_database, mysql_host, mysql_password, mysql_port, mysql_username

def query_database(sql_query):
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

        result = pd.read_sql_query(sql_query, conn)

        try:
            conn.close()
            print('Connection is closed')
        except:
            print('Connection is still open')

    return(result)




def drop_unsubscribed(frame):

    query = '''
        SELECT DISTINCT emailaddress FROM unsubscribed_email
    '''

    unsubscribed = query_database(query) 

    #drop all emails that have unsubscribed
    frame = frame.loc[~frame['email'].isin(unsubscribed['emailaddress'])]
    #drop all missing first names last names. Drop duplicates on emails
    frame = frame[(frame['firstname'] != '') & (frame['lastname'] != '')]
    frame = frame.drop_duplicates(subset=['email'])
    
    frame = frame.reset_index(drop = True)

    return(frame)




