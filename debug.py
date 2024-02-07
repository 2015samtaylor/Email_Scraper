# The email scrape filters for 12/16/2023 and on
#4285 emails in the inbox took 21 minutes
#Send out test emails for local baskebtall jsersyes
#Then send out for local football jerseys
#Still need to handle indirect replies

import logging
logging.basicConfig(filename='Email_Scraper.log', level=logging.INFO,
                   format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',force=True)

import pandas as pd
from config import imap_password_customplanet, db_username, db_password
from Scraping_Emails.modules.scrapes import scrape
from Scraping_Emails.modules.db_operations import DatabaseConnector
from SQL_Scripts.email_failures import update_bad_emails
from datetime import datetime, timedelta

email_address = 'team@customplanet.com'
email_pass = imap_password_customplanet
server = 'emailcampaign.c9vhoi6ncot7.us-east-1.rds.amazonaws.com'
database = 'emailcampaign'
db = 'emailcampaign'





# ----------------------------------Updating Faulty Emails in the DB before Send----------------------------------

#Searches GMAIL on the daily for bad emails that were sent back, and sends data to unsubscribed email table

def gather_and_send_bad_emails_to_db(subject_line, email_address, email_pass):

    #First thing to occur everytime
    logging.info('\n\nNew logging instance')

    current_date = datetime.now()
    previous_date = current_date - timedelta(days=1)
    formatted_date = previous_date.strftime('%m/%d/%Y')

 
    #Get all outbox emails based on subject line and start date
    msgs_outbox = scrape.scrape_msgs_outbox_or_inbox('outbox', subject_line, email_address, email_pass, formatted_date)
    outbox = scrape.create_msg_frame(msgs_outbox)
    outbox = scrape.cleanse_frame(outbox, 'outbox')

    # The date on this should be modern everyday once the initials are written
    failures = scrape.scrape_msgs_outbox_or_inbox('inbox', 'Delivery Status Notification', email_address, email_pass, formatted_date)
    failures = scrape.create_msg_frame(failures)

    if failures.empty != True:

        #This merge occurs in order to link the message_id on the failures, ultimately finding the emailaddress
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

        print(f'Updating bad emails table with {len(failures)} emails')
        logging.info(f'Updating bad emails table with {len(failures)} emails')

        update_bad_emails(failures)
    
    else:
        print('No emails to update')
        logging.info('No bad emails to update')
        

# ------------------------------------packaging process into final function----------------------------------------

def process(subject_line, email_address, email_pass, start_date):

    #create the msgs via scrape, then iterate through list of messages, and lastly cleanse frame
    email_address = 'team@customplanet.com'
    email_pass = imap_password_customplanet
 
    msgs_inbox = scrape.scrape_msgs_outbox_or_inbox('inbox', subject_line, email_address, email_pass, start_date)
    inbox = scrape.create_msg_frame(msgs_inbox)
    inbox = scrape.cleanse_frame(inbox, 'inbox')
    inbox.name = 'inbox'

    msgs_outbox = scrape.scrape_msgs_outbox_or_inbox('outbox', subject_line, email_address, email_pass, start_date)
    outbox = scrape.create_msg_frame(msgs_outbox)
    outbox = scrape.cleanse_frame(outbox, 'outbox')
    outbox['date'] = pd.to_datetime(outbox['date'], format='%Y-%m-%d')
    outbox.name = 'outbox'
        
    if inbox.empty == True:
        thread = pd.DataFrame()
        pass
    else: #this is a left merge on outbox
        thread = scrape.piece_together(outbox, inbox)
        thread = scrape.assign_sentiment(thread)
       
    # #If message was accidentally triggered more than once
    thread = thread.drop_duplicates(subset = ['subject', 'to'], keep='last')
    thread.reset_index(drop = True, inplace = True)

    return(inbox, outbox, thread)


subject_line = 'Official'
#Gathers and sends bad emails for yesterdays date. If the emails occured before then, 
# and there is an intermission period of running it will not update.
#Maybe run this piece in another script on the daily
gather_and_send_bad_emails_to_db(subject_line, email_address, email_pass)
inbox, outbox, thread= process(subject_line, email_address, email_pass, '11/15/2023')


#Instantiate the DatabaseConnector class
#Send over all emails in outbox variable to email_history table that contain the subject line 
#Optional column identifiers to add in to the DB
outbox['email_campaign_tag'] = 'Baseball Special'
outbox['sport'] = 'Baseball'
db_connector_email_history = DatabaseConnector(server, database, db_username, db_password, db, 'email_history')


#This looks for distinct email_ids first, and then sends. 
#If there is nothing in it, it will end everytime. 

db_connector_email_history.send(outbox, 'email_history')
