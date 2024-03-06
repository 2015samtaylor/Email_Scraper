import imaplib
import json
import pandas as pd
import email
import logging
from bs4 import BeautifulSoup, Comment
from textblob import TextBlob
import re
from datetime import datetime, timedelta
import numpy as np
# from config import db_username, db_password


class scrape:

    def scrape_msgs_outbox_or_inbox(inbox_or_outbox, subject_line, email_address, email_pass, start_date, log_type):

        # Convert start_date to IMAP date format
        start_date_formatted = datetime.strptime(start_date, '%m/%d/%Y').strftime('%d-%b-%Y')
        # end_date_formatted = (datetime.now() - timedelta(days=0)).strftime('%d-%b-%Y')

        # IMAP server settings for Gmail
        imap_server = 'imap.gmail.com'
        username = email_address
        password = email_pass

        # Connect to the Gmail IMAP server
        imap = imaplib.IMAP4_SSL(imap_server)
        imap.login(username, password)

        # to see what the mailbox names are, and what is available
        # status, mailboxes = imap.list()

        # Select the mailbox/folder where your emails are located
        
        if inbox_or_outbox == 'inbox':
            mailbox = 'INBOX'
            logging.info('Searching inbox')
        elif inbox_or_outbox == 'outbox':
            mailbox = '"[Gmail]/Sent Mail"'
            logging.info('Searching outbox')
        else:
            logging.info('Wrong string input for inbox or outbox')
            
        my_mail = imap.select(mailbox)

        # # Search for emails with a specific subject or other criteria
         # Search for emails with a specific subject and within the date range
        search_criteria = f'SUBJECT "{subject_line}" SINCE {start_date_formatted}'
        logging.info(search_criteria)
        status, response = imap.search(None, search_criteria)

        if status == 'OK':
            email_ids = response[0].split()
            #limit to 100 for testing
            # email_ids = email_ids[:100]
            if email_ids:
                print(f"{log_type} You have {len(email_ids)} email responses to the specified search criteria {subject_line} in the {inbox_or_outbox} with a filter date of {start_date}")
                logging.info(f"{log_type} You have email responses to the specified search criteria {subject_line} in the {inbox_or_outbox} with a filter date of {start_date}")
            else:
                print(f"{log_type} There are no responses to the specified emails search criteria {subject_line} in the {inbox_or_outbox} with a filter date of {start_date}")
                logging.info(f"{log_type} There are no responses to the specified emails search criteria {subject_line} in the {inbox_or_outbox} with a filter date of {start_date}")

        # ---------------------------iterate through email_ids, get the whole message and append the data to msgs list.

        msgs = [] 

        #Iterate through messages and extract data into the msgs list
        for num in email_ids:
            typ, data = imap.fetch(num, '(RFC822)') #RFC822 returns whole message (BODY fetches just body)

            msgs.append(data)

        return(msgs)
    

    #     -------------------------Cleanse the msgs list and extract what we want-------------------

                # if isinstance(response_part, bytes):
                #     my_msg = email.message_from_bytes(response_part)
                #     print(f'This is my message decoded from bytes {my_msg}')
                #     text_content = scrape.extract_text_from_email_bytes(my_msg)
                #     print(text_content)

                #     #If the text_content is empty, no reason to append. The email_data.append needs to be outside of this loop. Because it appends multiple empty text contents
                #     print('Email data has been appended from bytes')
                #     email_data.append(text_content)
    
    def decode_message(part_or_my_msg):
        
        try:
            body = part_or_my_msg.get_payload(decode=True).decode('utf-8')
        except UnicodeDecodeError:
            body = part_or_my_msg.get_payload(decode=True).decode('latin-1', 'replace')
        
        # If it's 'text/html', extract only the text content
        # if content_type in ['text/plain', 'text/html']:
        soup = BeautifulSoup(body, 'html.parser')

        #Clean HTML for NLP purposes and assign to reply_thread
        cleaned_text = soup.get_text(separator=' ', strip=True)
        return(cleaned_text)
       
                                



    def create_msg_frame(msgs):
        email_data = []

        for i, msg in enumerate(msgs[::-1]):  # start from the most recent message
            if isinstance(msg, tuple):
                response_part = msg
            else:   
                pass

            for response_part in msg:
              
              
                
                if isinstance(response_part, tuple):


                # if isinstance(msg_tuple, tuple) and all(isinstance(part, bytes) for part in msg_tuple):

                    # my_msg = email.message_from_bytes(response_part[1])
                    my_msg = email.message_from_bytes(response_part[1])

                    #maybe look into a header that has a delivery status here. 
                    email_dict = {
                        'subject': my_msg['subject'],
                        'from': my_msg['from'],
                        'to': my_msg['to'],
                        'date': my_msg['Date'],
                        'message_id' : my_msg['Message-ID'],
                        'references': my_msg['References'],
                        'in_reply_to': my_msg['In-Reply-To'],
                        'message_delivery': '',
                        'first_message': '',
                        'reply_thread': ''

                    }
                    #inbox messages will always be caught by multipart
                    if my_msg.is_multipart():
                        for part in my_msg.walk():
                            content_type = part.get_content_type()

                            #text/plain is initially available and then defaults to HTML.
                            # Check for both 'text/plain' and 'text/html' and get the body.  is ignored
                            if content_type in ['text/html']:  #'text/plain'

                                cleaned_text = scrape.decode_message(part)
                                email_dict['reply_thread'] = cleaned_text

                            #This bit is present for some automated emails systems notifying of rejection. Maybe think about removing from 
                            elif content_type in ['multipart/report']:

                                # The multipart/report may have subparts
                                for subpart in part.walk():
                                    if subpart.get_content_type() == "message/delivery-status":

                                        subpart_payload = subpart.get_payload(i=1)
                                        message_status = subpart_payload._headers[1]
                                        email_dict['message_delivery'] = message_status

                                    else:
                                        pass
                              
                            #outbox defaults to the else block everytime
                    else:   #scraping outbox will never be multipart, so this is where the first message is needed
                        cleaned_text = scrape.decode_message(my_msg)
                        email_dict['first_message'] = cleaned_text

                    #append email_dict at the end no matter what
                    email_data.append(email_dict)

        df = pd.DataFrame(email_data)

        return(df)
        
    def cleanse_frame(df, inbox_or_outbox):
            
        try:
            #change date to datetime, in order to create unique _id reference of when the email occured
            df['date'] = pd.to_datetime(df['date'], errors='coerce', utc=True)
            # df['date'] = df['date'].apply(lambda x: x.isoformat())
                  
            # Create a new column that shows 'Y' if the message is a reply, 'N' otherwise
            df['reply'] = np.where(~df['references'].isna(), 'Y', 'N')


            #Remove 'RE:' from the 'subject' column in order to merge on subject line
            df['subject'] = df['subject'].str.replace(r'^RE:\s*', '', case=False, regex=True)
            #Remove 'FWD:' and 'FW:' from the 'subject' column
            df['subject'] = df['subject'].str.replace(r'^FWD:\s*', '', case=False, regex=True)
            df['subject'] = df['subject'].str.replace(r'^FW:\s*', '', case=False, regex=True)
            df['subject'] = df['subject'].str.strip()

            #extract emails addresses from to & from columns
            df['to'] = df['to'].apply(lambda x: re.search(r'<([^<>]+)>', x).group(1) if '<' in x and '>' in x else x)
            df['from'] = df['from'].apply(lambda x: re.search(r'<([^<>]+)>', x).group(1) if '<' in x and '>' in x else x)

        except (KeyError, TypeError) as e:
            pass
    
        except Exception as e:
            print(f"An unexpected error occurred: {type(e).__name__} - {e}")
        
        
        if inbox_or_outbox == 'outbox':
            try:
                #make the body column a list
                df['body'] = df['body'].apply(lambda x: [x] if isinstance(x, str) else x)

                df = df[['message_id', 'subject', 'from', 'to', 'date', 'first_message', 'email_campaign_tag', 'sport']]
                # df['date'] = pd.to_datetime(df['date'])        
                df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
            
            except KeyError:
                pass
            
                    
        elif inbox_or_outbox == 'inbox':
            try:
                # Drop empty messages based on body
                df = df.dropna(subset=['first_message'], how='any')
                df = df.sort_values(by=['subject','date'], ascending=False)
                # Drop duplicates in the 'subject' column, keeping only the first occurrence (most recent)
                # Only keep the most latest thread, and attach it into the outbox body array
                df = df.drop_duplicates(subset='subject', keep='first').reset_index(drop = True)
            
            except KeyError:
                pass
        else:
            print('Wrong inbox or outbox variable')
            logging.info('Wrong inbox or outbox variable')
                
        return(df)


        
    # ------------------------------------------Piece together replies to outbox emails------------------------------- 

    def piece_together(outbox, inbox):

        box = pd.merge(inbox, outbox, left_on = 'references', right_on='message_id', how = 'right', suffixes=('_inbox', '_outbox'))

        box = box[['message_id_outbox', 'references_inbox', 'in_reply_to_inbox', 'subject_outbox', 'from_outbox', 'to_outbox',
            'date_outbox', 'first_message_outbox', 'reply_inbox', 'reply_thread_inbox']]

        box = box.rename(columns = {'subject_outbox': 'subject', 'from_outbox': 'from', 'to_outbox': 'to', 'message_id_outbox': 'message_id',
            'date_outbox': 'date', 'first_message_outbox': 'first_message', 'reply_inbox': 'reply', 'reply_thread_inbox': 'reply_thread'})

        box['reply'] = box['reply'].fillna('N')
        box['reply_thread'] = box['reply_thread'].fillna('')

        box['date'] = pd.to_datetime(box['date'])

        return(box)

    
    def assign_sentiment(thread):

        # Assuming 'df' is your DataFrame and 'text_column' is the column with text data
        thread['sentiment'] = thread['reply_thread'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
        
        # You can categorize the sentiment if needed
        thread['sentiment_category'] = pd.cut(thread['sentiment'], bins=3, labels=['negative', 'neutral', 'positive'])

        # # Display the DataFrame with sentiment scores
        thread.loc[(thread['sentiment'] == 0) & (thread['reply'] == 'N'), 'sentiment_category'] = None

        #drop everything that does not have a recipient_id
        thread = thread[~thread['references_inbox'].isna()]

        return(thread)
    
    
    def extract_text_from_email_bytes(msg):
        text = ""

    
        # Walk through the email's payload
        for part in msg.walk():
                
                if part.get_content_type() == "multipart/alternative":
            
                    for alternative_part in part.get_payload():
        
                            if alternative_part.get_content_type() == 'text/html':

                
                                    # Extract text content from HTML parts
                                    html_content = alternative_part.get_payload(decode=True).decode(
                                            alternative_part.get_content_charset() or "utf-8", "ignore"
                                    )
                                    soup = BeautifulSoup(html_content, "html.parser")
                                    # Convert HTML to plain text using BeautifulSoup

                                    uuid_input = soup.find_all('input', {'id': lambda x: x and 'hidden-uuid' in x})
                                    print('UUID input found in bytes email' + str(uuid_input))

                                    output =  soup.get_text(separator="\n", strip=True)

                                    

                                    text += output

                            else:
                                    pass

        return(text)
    

    def map_reply_outbox(thread, outbox):
        try:
            if not thread.empty:
                reply_dict = thread.set_index('message_id')['reply'].to_dict()
                outbox['reply'] = outbox['message_id'].map(reply_dict).fillna('N')
            else:
                logging.info('Thread dataframe is empty')
        except Exception as e:
            logging.error(f'Error in map_reply_outbox: {e}')

        return(outbox)
    




    # class EmailConfig:
    # def __init__(self, SMTP_CONN, EMAIL_ADDRESS_FROM, EMAIL_PASS, df, contact_column, sport, email_campaign_name,email_subject_line, server, database, table_name):
     
    #     self.EMAIL_ADDRESS_FROM = EMAIL_ADDRESS_FROM
    #     self.EMAIL_PASS = EMAIL_PASS
        
    #     self.SMTP_CONN = SMTP_CONN
    #     self.df = df

    #     self.contact_column = contact_column
    #     self.sport = sport
    #     self.email_campaign_name = email_campaign_name
    #     self.email_subject_line = email_subject_line
    #     # self.template = template
    
    #     self.server = server
    #     self.database = database
    #     self.table_name = table_name

       


