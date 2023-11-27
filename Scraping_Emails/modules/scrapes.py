import imaplib
import json
import pandas as pd
import email
import logging
from bs4 import BeautifulSoup
import re
from config import imap_password_customplanet, db_username, db_password
email_address = 'team@customplanet.com'

class scrape:

    def scrape_msgs_outbox_or_inbox(inbox_or_outbox, subject_line):

        # IMAP server settings for Gmail
        imap_server = 'imap.gmail.com'
        username = email_address
        password = imap_password_customplanet

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
                print(f"You have email responses to the specified search criteria {subject_line} in the {inbox_or_outbox}")
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
                        'subject': my_msg['subject'],
                        'from': my_msg['from'],
                        'to': my_msg['to'],
                        'date': my_msg['Date'],
                        'first_message': '',
                        'reply_thread': ''
                    }

                    if my_msg.is_multipart():
                        for part in my_msg.walk():
                            content_type = part.get_content_type()

                            # Check for both 'text/plain' and 'text/html'
                            if content_type in ['text/plain', 'text/html']:
                                try:
                                    body = part.get_payload(decode=True).decode('utf-8')
                                except UnicodeDecodeError:
                                    body = part.get_payload(decode=True).decode('latin-1', 'replace')

                                # If it's 'text/html', extract only the text content
                                if content_type == 'text/html':
                                    soup = BeautifulSoup(body, 'html.parser')
                                    body = soup.get_text(separator='\n', strip=True)

                                email_dict['first_message'] = body
                                break  # Assuming you want only the first plain text or HTML body

                    else:
                        # If it's not multipart, try to get the payload directly
                        try:
                            body = my_msg.get_payload(decode=True).decode('utf-8')
                        except UnicodeDecodeError:
                            body = my_msg.get_payload(decode=True).decode('latin-1', 'replace')
                        email_dict['first_message'] = body

                    email_data.append(email_dict)

        df = pd.DataFrame(email_data)

        return(df)

    
    def cleanse_frame(df, inbox_or_outbox):
            
        try:
            #change date to datetime, in order to create unique _id reference of when the email occured
            df['date'] = pd.to_datetime(df['date'], errors='coerce', utc=True)
            df['recipient_id'] = df['date'].dt.strftime('%m%d%Y%H%M%S')
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

    #Three things need to happen to be pieced together
    # 1. subject of inbox message contains sent message subject
    # 2. Message must be a RE:
    # 3. The outbox 'to' email must be the same as inbox 'from' email


    def piece_together(outbox, inbox):

        for i in range(len(outbox)):
            idx_ref = outbox.iloc[i]
            sent_message_subject = idx_ref['subject']
            sent_message_to = idx_ref['to']

            try:
                # Move the entire block of code inside the try block
                message = inbox.loc[(inbox['subject'].str.contains(sent_message_subject, case=False, regex=True)) & (inbox['reply'] == 'Y')]

                # check if the initial sent to address is the same as the reply from. (Confirming the reply)
                if not message.empty:
                    if message['from'].values[0] == sent_message_to:
                        pass
                    else:
                        message = message.drop(index=message.index)

                body = message['first_message'].values[0]
                date = str(message['date'].values[0])

                re_dict = {
                    'date': date,
                    'thread': body
                }

                re_dict = json.dumps(re_dict)

                outbox.loc[i, 'reply_thread'] = re_dict
                outbox.loc[i, 'reply'] = 'Y'

            except (KeyError, IndexError):
                print('Inbox is empty')

        return(outbox)

