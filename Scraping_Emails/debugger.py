# The email scrape filters for 12/16/2023 and on
import logging
import pandas as pd
from config import imap_password_customplanet, db_username, db_password
from modules.scrapes import scrape
from modules.db_operations import DatabaseConnector

email_address = 'team@customplanet.com'
email_pass = imap_password_customplanet


logging.basicConfig(filename='Email_Scraper.log', level=logging.INFO,
                   format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',force=True)


# ------------------------------------packaging process into final function----------------------------------------

def process(subject_line, email_address, email_pass, start_date):

    logging.info('\n\nNew logging instance')

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
    outbox.name = 'outbox'
    
    if inbox.empty == True:
        thread = pd.DataFrame()
        pass
    else: #this is a left merge on outbox
        thread = scrape.piece_together(outbox, inbox)
        thread = scrape.assign_sentiment(thread)
    
    # #If message was accidentally triggered more than once
    thread = thread.drop_duplicates(subset = ['subject', 'to'], keep='last')
    
    # # Specify your database connection details
    # server = 'emailcampaign.c9vhoi6ncot7.us-east-1.rds.amazonaws.com'
    # database = 'emailcampaign'
    # db = 'emailcampaign'
    # table_name = 'thread'

    # # Instantiate the DatabaseConnector class
    # db_connector = DatabaseConnector(server, database, db_username, db_password, db, table_name)

    # #If there are any new records, append them onto thread table
    # #Update the reply_thread everytime
    # if thread.empty != True:
    #     new_records = db_connector.append_new_records(thread)
    #     db_connector.update_reply_thread(thread)
    # else:
    #     logging.info('Thread is an empty frame')
    #     print('Thread is an empty frame')
    #     new_records = None

    # return(inbox, outbox, thread)

    return(msgs_outbox, outbox)

# The foreign constraint enforces that this must have been sent initially. 
# inbox, outbox, thread = process('Official', email_address, email_pass, '11/15/2023')
msgs_outbox, outbox = process('Official', email_address, email_pass, '11/15/2023')


#4285 emails in the inbox took 21 minutes
#Send out test emails for local baskebtall jsersyes
#Then send out for local football jerseys
# The scrape subject line, and email subject line should be referencing one variable