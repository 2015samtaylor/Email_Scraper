from datetime import datetime
import logging
import pandas as pd
from config import imap_password_customplanet, db_username, db_password
from Scraping_Emails.modules.scrapes import scrape
from Scraping_Emails.modules.db_operations import DatabaseConnector
from SQL_Scripts.email_failures import update_bad_emails


def gather_and_send_bad_emails():

    email_address = 'team@customplanet.com'
    email_pass = imap_password_customplanet
    subject_line = 'Official'
    start_date = '11/15/2023'  #this can eventually be the current day once automated. 

    #Get all outbox emails based on subject line and start date
    msgs_outbox = scrape.scrape_msgs_outbox_or_inbox('outbox', subject_line, email_address, email_pass, start_date)
    outbox = scrape.create_msg_frame(msgs_outbox)
    outbox = scrape.cleanse_frame(outbox, 'outbox')

    # The date on this should be modern everyday once the initials are written
    failures = scrape.scrape_msgs_outbox_or_inbox('inbox', 'Delivery Status Notification', email_address, email_pass, '11/15/2023')
    failures = scrape.create_msg_frame(failures)

    failures = failures[['message_id', 'references']]
    failures.rename(columns = {'message_id': 'message_id_failed', 'references': 'references_failed'}, inplace = True)
    failures = pd.merge(outbox, failures, left_on='message_id', right_on='references_failed')
    failures.rename(columns = {'to': 'emailaddress'}, inplace = True)

    #Maybe write directly to the customer table
    failures = failures[['emailaddress']].drop_duplicates().reset_index(drop = True)

    # Get current date and time
    current_datetime = datetime.now()
    formatted_date = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    failures['created_at'] = formatted_date
    # Convert the 'created_at' column to datetime format if it's not already
    failures['created_at'] = pd.to_datetime(failures['created_at'])

    update_bad_emails(failures)

gather_and_send_bad_emails()
