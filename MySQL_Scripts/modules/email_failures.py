#Inserting Faulty Emails
import pandas as pd
from sshtunnel import SSHTunnelForwarder
import pymysql
from pymysql import Error
from config import ssh_username, ssh_host, ssh_password, ssh_port, mysql_database, mysql_host, mysql_password, mysql_port, mysql_username
from datetime import datetime
import logging

from config import imap_password_customplanet, db_username, db_password
from Scraping_Emails.modules.scrapes import scrape
from Scraping_Emails.modules.db_operations_aws import DatabaseConnector
from MySQL_Scripts.modules.email_failures import *
from datetime import datetime, timedelta


def find_bad_emails(outbox, failures, subject_line):
        
        try:
            #This merge occurs in order to link the message_id on the failures, ultimately finding the emailaddress
            failures = failures[['message_id', 'references']]
            failures = failures.rename(columns = {'message_id': 'message_id_failed', 'references': 'references_failed'})

            #When outbox is empty here, failures is still present

            if outbox.empty:
                logging.info('No messages brought back from the outbox with {subject_line}, can not link up to find bad emails')
            else:
                pass

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
            print(f'No bad emails to update with {subject_line}')
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
            logging.info('All new emails sent updated succesfully')
        
        except Exception as e:
            print(f'Second except block An error occured: {e}')
            logging.info(f'Second except block An error occured: {e}')
        
        finally:
            conn.close()



# ----------------------------------Updating Faulty Emails in the DB before Send----------------------------------
#Searches GMAIL on the daily for bad emails that were sent back, and sends data to unsubscribed email table

def gather_and_send_bad_emails_to_db(subject_line, email_address, email_pass, log_type, override_date = None):

    #First thing to occur everytime
    logging.info('\n\nNew logging instance')

    current_date = datetime.now()

    if override_date:
        previous_date = datetime.strptime(override_date, '%m/%d/%Y').date()
    else:
        previous_date = current_date - timedelta(days=1)

    formatted_date = previous_date.strftime('%m/%d/%Y')
    #The reason the date is up today is because the faulty emails from the past are already in the DB

    #Get all outbox emails based on subject line and start date
    msgs_outbox = scrape.scrape_msgs_outbox_or_inbox('outbox', subject_line, email_address, email_pass, formatted_date, log_type)
    outbox = scrape.create_msg_frame(msgs_outbox)
    # outbox = scrape.cleanse_frame(outbox, 'outbox')

    # Find emails with delivery status notification flags, link those to what was sent, and write those emails to the CP db
    failures = scrape.scrape_msgs_outbox_or_inbox('inbox', 'Delivery Status Notification', email_address, email_pass, formatted_date, log_type)
    failures = scrape.create_msg_frame(failures)

    #givne the fact that its iterating through subject lines there will always be something for outbox or failures
    failures = find_bad_emails(outbox, failures, subject_line)

    if failures.empty != True:
        #the merge is returning nothing here causing update to occur anyways. Debug this portion and figure out the logic
        update_bad_emails(failures)
    
    else:
        print('No emails to update')
        logging.info('No bad emails to update')

    return(failures)
