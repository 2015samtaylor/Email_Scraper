import smtplib
from email.message import EmailMessage
import logging
import pandas as pd
import os
from Sending_Emails.modules.html_email_strings.baseball_intro import get_intro_template   #Dictates what template is being passed in into the body variable




#Change that needs to occur, same conn needs to be used in blast func




class SendMail:


    def get_smtp_connection(EMAIL_ADDRESS_FROM, EMAIL_PASS):
        # Establish the SMTP connection
        smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp.login(EMAIL_ADDRESS_FROM, EMAIL_PASS)
        logging.info('SMTP connection created')
        return(smtp)
    
    #OLD PROCESS
    #  with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        #   smtp.login(EMAIL_ADDRESS_FROM, EMAIL_PASS)
        #   smtp.send_message(msg)


    def send(SMTP_CONN, EMAIL_ADDRESS_FROM, EMAIL_PASS, global_subject_line, school, sport, email):
        msg = EmailMessage()
        msg['Subject'] = global_subject_line.format(sport, school)
        msg['From'] = EMAIL_ADDRESS_FROM
        msg['To'] = email

        # Read the PNG file as binary data and encode it as base64
        # png_file_path = f'PNGs/{png_path}.png'
        # try:
        #     with open(png_file_path, 'rb') as f:
        #         image_data = f.read()
        #         image_base64 = base64.b64encode(image_data).decode('utf-8')
        # except FileNotFoundError:
        #     image_base64 = ''
            
        body = get_intro_template()

        # Set the content as HTML
        msg.set_content(body, subtype='html')

        try:
            SMTP_CONN.send_message(msg)

        except smtplib.SMTPRecipientsRefused as e:
            # Handle the specific exception
            print(f"Recipient error for {email}: {e}")
        
# -------------------------------------------------------------------------------------------

    #Different logic, output.csv is not created yet. It is at the point of blasting the first 5-. 
    #get next 50 is modified with a try except where the except simply gets the first 50. 
    #Attempts to read from the output.csv everytime   

    def get_next_50(df):

        try:    
            email_history = pd.read_csv(os.getcwd() + '\\output.csv')

            last_email_sent = email_history['contact_email'].iloc[-1]
                
            # Find the index in df where the 'email' column matches the last_email_sent
            index_to_start = df[df['email'] == last_email_sent].index.max() + 1
                
            # # Process df starting from the index_to_start
            df_remaining = df.loc[index_to_start: index_to_start + 50]

        except FileNotFoundError:
            print('Output is not created, first run of 50 emails preparing to be sent')
            logging.info('Output is not created, first run of 50 emails preparing to be sent')

            # # Process df starting from the index_to_start
            df_remaining = df.iloc[0:50]

        except TypeError:
            
            #email where final send was left off can not be matched up in the original df
            print('Email where final send was left off can not be matched up in the original df. Frame is empty')
            logging.info('Email where final send was left off can not be matched up in the original df. Frame is empty')
            #create empty frame to return
            df_remaining = pd.DataFrame()

        return(df_remaining)





