import smtplib
from email.message import EmailMessage
# import imghdr
# import base64
import pandas as pd
import os
from modules.html_email_strings.baseball_intro import get_intro_template


class SendMail:


    def send(EMAIL_ADDRESS_FROM, EMAIL_PASS, global_subject_line, school, sport, email, unique_identifier):
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
            
        body = get_intro_template(school, unique_identifier, sport)

        # body = schools_intro_template.format(school, unique_identifier, sport)

        # Set the content as HTML
        msg.set_content(body, subtype='html')

        try:
             
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(EMAIL_ADDRESS_FROM, EMAIL_PASS)
                smtp.send_message(msg)
            
        except smtplib.SMTPRecipientsRefused as e:
            # Handle the specific exception
            print(f"Recipient error for {email}: {e}")
        
        # except Exception as e:
        #     # Handle other exceptions
        #     print(f"An error occurred: {e}")


    def get_next_50(email_history=None):

        df = pd.read_csv(r'C:\Users\samuel.taylor\OneDrive - Green Dot Public Schools\Desktop\Git_Directory\CP\CustomPlanet_Work\Email_Scraper\SQL_Scripts\email_prospects_csvs\baseball.csv')
        df = df.drop_duplicates(subset='email')
        df = df.reset_index(drop = True)

    
        #this means email_history is undeclared as a variable, the process broke. Start by reading in the csv   
        if email_history is None:
            email_history = pd.read_csv(os.getcwd() + '\\output.csv')

        last_email_sent = email_history['contact_email'].iloc[-1]
            
        # Find the index in df where the 'email' column matches the last_email_sent
        index_to_start = df[df['email'] == last_email_sent].index.max() + 1

        # # Process df starting from the index_to_start
        df_remaining = df.iloc[index_to_start: index_to_start + 50]
        
        return(df_remaining)





