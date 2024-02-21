import pandas as pd
from config import imap_password_customplanet, db_username, db_password
from Scraping_Emails.modules.scrapes import scrape
from Scraping_Emails.modules.db_operations_aws import DatabaseConnector
from SQL_Scripts.modules.email_failures import *
from datetime import datetime, timedelta

# ----------------------------------Updating Faulty Emails in the DB before Send----------------------------------
#Searches GMAIL on the daily for bad emails that were sent back, and sends data to unsubscribed email table

def gather_and_send_bad_emails_to_db(subject_line, email_address, email_pass):

    #First thing to occur everytime
    logging.info('\n\nNew logging instance')

    current_date = datetime.now()
    previous_date = current_date - timedelta(days=1)
    # formatted_date = previous_date.strftime('%m/%d/%Y')
    formatted_date = '11/01/2023'
    #The reason the date is up today is because the faulty emails from the past are already in the DB


    #Get all outbox emails based on subject line and start date
    msgs_outbox = scrape.scrape_msgs_outbox_or_inbox('outbox', subject_line, email_address, email_pass, formatted_date)
    outbox = scrape.create_msg_frame(msgs_outbox)
    outbox = scrape.cleanse_frame(outbox, 'outbox')

    # Find emails with delivery status notification flags, link those to what was sent, and write those emails to the CP db
    failures = scrape.scrape_msgs_outbox_or_inbox('inbox', 'Delivery Status Notification', email_address, email_pass, formatted_date)
    failures = scrape.create_msg_frame(failures)

    failures = find_bad_emails(outbox, failures, subject_line)
    
    #failures will return as None if except block is hit
    if failures is not None:
        print(len(failures))
        #the merge is returning nothing here causing update to occur anyways. Debug this portion and figure out the logic
        update_bad_emails(failures)
    
    else:
        print('No emails to update')
        logging.info('No bad emails to update')


email_address = 'team@customplanet.com'
email_pass = imap_password_customplanet
server = 'emailcampaign.c9vhoi6ncot7.us-east-1.rds.amazonaws.com'
database = 'emailcampaign'
db = 'emailcampaign'

db_connector_email_history = DatabaseConnector(server, database, db_username, db_password, db, 'email_history')
query = db_connector_email_history.SQL_query('SELECT DISTINCT subject FROM [emailcampaign].[dbo].[email_history]')


#Iterate through all unique subject lines to update the db table with all faulty email addresses
for line in query['subject']:
    print(line)
    gather_and_send_bad_emails_to_db(line, email_address, email_pass)
