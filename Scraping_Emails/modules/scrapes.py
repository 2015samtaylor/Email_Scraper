import imaplib
import json
import pandas as pd
import email
import logging
from bs4 import BeautifulSoup, Comment
import re
db_username = 'admin'
db_password = 'Pretty11'
# from config import db_username, db_password


class scrape:

    def scrape_msgs_outbox_or_inbox(inbox_or_outbox, subject_line, email_address, email_pass):

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
        elif inbox_or_outbox == 'outbox':
            mailbox = '"[Gmail]/Sent Mail"'
        else:
            logging.info('Wrong string input for inbox or outbox')
            
        my_mail = imap.select(mailbox)

        # # Search for emails with a specific subject or other criteria
        search_criteria = f'SUBJECT "{subject_line}"'
        status, response = imap.search(None, search_criteria)

        if status == 'OK':
            email_ids = response[0].split()
            if email_ids:
                print(f"You have {len(email_ids)} email responses to the specified search criteria {subject_line} in the {inbox_or_outbox}")
                logging.info(f"You have email responses to the specified search criteria {subject_line} in the {inbox_or_outbox}")
            else:
                print(f"There are no responses to the specified emails search criteria {subject_line} in the {inbox_or_outbox}")
                logging.info(f"There are no responses to the specified emails search criteria {subject_line} in the {inbox_or_outbox}")

        # ---------------------------iterate through email_ids, get the whole message and append the data to msgs list.

        msgs = [] 

        #Iterate through messages and extract data into the msgs list
        for num in email_ids:
            typ, data = imap.fetch(num, '(RFC822)') #RFC822 returns whole message (BODY fetches just body)

            msgs.append(data)

        return(msgs)

    #     -------------------------Cleanse the msgs list and extract what we want-------------------

    def create_msg_frame(msgs):
        email_data = []

        for msg in msgs[::-1]:  # start from the most recent message
            for response_part in msg:
                if isinstance(response_part, tuple):

                    my_msg = email.message_from_bytes(response_part[1])

                    email_dict = {
                        'recipient_id': '',
                        'subject': my_msg['subject'],
                        'from': my_msg['from'],
                        'to': my_msg['to'],
                        'date': my_msg['Date'],
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
                                try:
                                    body = part.get_payload(decode=True).decode('utf-8')
                                except UnicodeDecodeError:
                                    body = part.get_payload(decode=True).decode('latin-1', 'replace')
                                
                                # If it's 'text/html', extract only the text content
                                # if content_type in ['text/plain', 'text/html']:
                                soup = BeautifulSoup(body, 'html.parser')

                                #Clean HTML for NLP purposes and assign to reply_thread
                                cleaned_text = soup.get_text(separator=' ', strip=True)
                                email_dict['reply_thread'] = cleaned_text
                                
                                uuid_input = soup.find_all('input', {'id': lambda x: x and 'hidden-uuid' in x})

                                # Check if any UUID input is found
                                if uuid_input:
                                    uuid = uuid_input[0]['value']
                                    email_dict['recipient_id'] = uuid
                                else:
                                    pass
                                    #no uuid
                                break  #As to not continue on to other multiparts

                            #outbox defaults to the else block everytime
                    else:   #scraping outbox will never be multipart, so this is where the first message is needed
                        # Get the payload directly
                        try:
                            body = my_msg.get_payload(decode=True).decode('utf-8')
                        except UnicodeDecodeError:
                            body = my_msg.get_payload(decode=True).decode('latin-1', 'replace')
                        
                        soup = BeautifulSoup(body, 'html.parser')

                        #Clean HTML for NLP purposes and assign to reply_thread
                        cleaned_text = soup.get_text(separator=' ', strip=True)
                        email_dict['first_message'] = cleaned_text

                        uuid_input = soup.find_all('input', {'id': lambda x: x and 'hidden-uuid' in x})

                        # Check if any UUID input is found
                        if uuid_input:
                            uuid = uuid_input[0]['value']
                            email_dict['recipient_id'] = uuid
                        else:
                            pass
                            #no uuid

                    #append email_dict at the end no matter what
                    email_data.append(email_dict)

        df = pd.DataFrame(email_data)

        return(df, soup)
        
    def cleanse_frame(df, inbox_or_outbox):
            
        try:
            #change date to datetime, in order to create unique _id reference of when the email occured
            df['date'] = pd.to_datetime(df['date'], errors='coerce', utc=True)
            df['date'] = df['date'].apply(lambda x: x.isoformat())
            

            #create a new column that shows 1 if the message is a reply
            # df['reply'] = np.where(df['subject'].str.contains('RE:', case=False, regex=True), 'Y', 'N')
            # Create a new column that shows 'Y' if the message is a reply, 'N' otherwise
            df['reply'] = df['subject'].apply(lambda x: 'Y' if 'RE:' in x.upper() else 'N')


            #Remove 'RE:' from the 'subject' column in order to merge on subject line
            df['subject'] = df['subject'].str.replace(r'^RE:\s*', '', case=False, regex=True)
            #Remove 'FWD:' and 'FW:' from the 'subject' column
            df['subject'] = df['subject'].str.replace(r'^FWD:\s*', '', case=False, regex=True)
            df['subject'] = df['subject'].str.replace(r'^FW:\s*', '', case=False, regex=True)
            df['subject'] = df['subject'].str.strip()

            #extract emails addresses from to & from columns
            df['to'] = df['to'].apply(lambda x: re.search(r'<([^<>]+)>', x).group(1) if '<' in x and '>' in x else x)
            df['from'] = df['from'].apply(lambda x: re.search(r'<([^<>]+)>', x).group(1) if '<' in x and '>' in x else x)
        
        except KeyError:
            pass
        
        
        if inbox_or_outbox == 'outbox':
            try:
                #make the body column a list
                df['body'] = df['body'].apply(lambda x: [x] if isinstance(x, str) else x)
                
            
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

        box = pd.merge(outbox, inbox, on = 'recipient_id', how = 'left', suffixes=('_outbox', '_inbox'))

        box = box[['recipient_id', 'subject_outbox', 'from_outbox', 'to_outbox',
            'date_outbox', 'first_message_outbox', 'reply_inbox', 'reply_thread_inbox']]

        box = box.rename(columns = {'subject_outbox': 'subject', 'from_outbox': 'from', 'to_outbox': 'to',
            'date_outbox': 'date', 'first_message_outbox': 'first_message', 'reply_inbox': 'reply', 'reply_thread_inbox': 'reply_thread'})

        box['reply'] = box['reply'].fillna('N')
        box['reply_thread'] = box['reply_thread'].fillna('')

        box['date'] = pd.to_datetime(box['date'])

        return(box)

