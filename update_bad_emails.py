import pandas as pd
from config import imap_password_customplanet, db_username, db_password
from Scraping_Emails.modules.scrapes import scrape
from Scraping_Emails.modules.db_operations import DatabaseConnector
from SQL_Scripts.email_failures import *
from datetime import datetime, timedelta

# ----------------------------------Updating Faulty Emails in the DB before Send----------------------------------
#Searches GMAIL on the daily for bad emails that were sent back, and sends data to unsubscribed email table

def gather_and_send_bad_emails_to_db(subject_line, email_address, email_pass):

    #First thing to occur everytime
    logging.info('\n\nNew logging instance')

    current_date = datetime.now()
    previous_date = current_date - timedelta(days=1)
    formatted_date = previous_date.strftime('%m/%d/%Y')
    #The reason the date is up today is because the faulty emails from the past are already in the DB


    #Get all outbox emails based on subject line and start date
    msgs_outbox = scrape.scrape_msgs_outbox_or_inbox('outbox', subject_line, email_address, email_pass, formatted_date)
    outbox = scrape.create_msg_frame(msgs_outbox)
    outbox = scrape.cleanse_frame(outbox, 'outbox')

    # Find emails with delivery status notification flags, link those to what was sent, and write those emails to the CP db
    failures = scrape.scrape_msgs_outbox_or_inbox('inbox', 'Delivery Status Notification', email_address, email_pass, formatted_date)
    failures = scrape.create_msg_frame(failures)

    #givne the fact that its iterating through subject lines there will always be something for outbox or failures
    failures = find_bad_emails(outbox, failures, subject_line)

    if failures.empty != True:
        #the merge is returning nothing here causing update to occur anyways. Debug this portion and figure out the logic
        update_bad_emails(failures)
    
    else:
        print('No emails to update')
        logging.info('No bad emails to update')
