#2000 emails sent to email_history took 5 minutes
import logging
import warnings
import os

# Mute pandas UserWarning
warnings.filterwarnings("ignore", category=UserWarning, module="pandas")

#create log dir and file
logpath_creation = os.getcwd() + '\\Logs'
if not os.path.exists(logpath_creation):
    os.makedirs(logpath_creation)

logging.basicConfig(filename= logpath_creation + '\\Email_Scraper.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', force=True)


import pandas as pd
from config import imap_password_customplanet, db_username, db_password
from Scraping_Emails.modules.scrapes import scrape
from Scraping_Emails.modules.db_operations_aws import DatabaseConnector

#What is the difference between update_bad_emails & gather and send bad emails to db
#Consolidating update_bad_emails to email_faulures


email_address = 'team@customplanet.com'
email_pass = imap_password_customplanet
server = 'emailcampaign.c9vhoi6ncot7.us-east-1.rds.amazonaws.com'
database = 'emailcampaign'
db = 'emailcampaign'

# ------------------------------------packaging process into final function----------------------------------------

def process(subject_line, email_address, email_pass, start_date):

    #create the msgs via scrape, then iterate through list of messages, and lastly cleanse frame
    email_address = 'team@customplanet.com'
    email_pass = imap_password_customplanet

    #First thing to occur everytime
    logging.info('\n\nNew logging instance')
 
    msgs_inbox = scrape.scrape_msgs_outbox_or_inbox('inbox', subject_line, email_address, email_pass, start_date, 'Current Subject Line')
    inbox = scrape.create_msg_frame(msgs_inbox)
    inbox = scrape.cleanse_frame(inbox, 'inbox')
    inbox.name = 'inbox'

    msgs_outbox = scrape.scrape_msgs_outbox_or_inbox('outbox', subject_line, email_address, email_pass, start_date, 'Current Subject Line')
    outbox = scrape.create_msg_frame(msgs_outbox)
    outbox = scrape.cleanse_frame(outbox, 'outbox')
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
    outbox = scrape.map_reply_outbox(thread, outbox)

    return(inbox, outbox, thread)


# -------------------------------------------

#Get inbox, outbox, and create thread with given subject line back to given date
subject_line = 'Official MLB Jerseys'
inbox, outbox, thread= process(subject_line, email_address, email_pass, '02/01/2024')


# Instantiate the DatabaseConnector class, send over all emails in outbox variable to email_history table that contain the subject line 
#Optional column identifiers to add in to the DB
outbox['email_campaign_tag'] = 'Majestic Round 2'
outbox['sport'] = 'Baseball'    #frame   #table_name
db_connector_email_history = DatabaseConnector(server, database, db_username, db_password, db, 'email_history')



if outbox.empty != True:
    db_connector_email_history = DatabaseConnector(server, database, db_username, db_password, db, 'email_history')
    db_connector_email_history.send(outbox, 'email_history')
else:
    logging.info('Outbox is an empty frame')
    print('Outbox is an empty frame')