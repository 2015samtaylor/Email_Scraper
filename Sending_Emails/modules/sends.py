import smtplib
from email.message import EmailMessage
import logging
import pandas as pd
import time
import os
from datetime import datetime
import pytz
import time
import base64
from Sending_Emails.modules.html_email_strings.schools_sport_focus import get_template 
# from Sending_Emails.modules.html_email_strings.baseball_intro import get_intro_template   #Dictates what template is being passed in into the body variable


class SendMail:


    def get_smtp_connection(EMAIL_ADDRESS_FROM, EMAIL_PASS):
        # Establish the SMTP connection
        smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp.login(EMAIL_ADDRESS_FROM, EMAIL_PASS)
        logging.info('SMTP connection created')
        return(smtp)
    
    def pass_in_png(png_path):
            # Read the PNG file as binary data and encode it as base64
        png_file_path = f'PNGs/{png_path}.png'
        try:
            with open(png_file_path, 'rb') as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
        except FileNotFoundError:
            image_base64 = ''

        return(image_base64)


    def send(email_config, email_contact, school = None):

        EMAIL_ADDRESS_FROM = email_config.EMAIL_ADDRESS_FROM
        EMAIL_PASS = email_config.EMAIL_PASS
        SMTP_CONN = email_config.SMTP_CONN
    
        contact_column = email_config.contact_column
        sport = email_config.sport
        email_campaign_name = email_config.email_campaign_name
        email_subject_line = email_config.email_subject_line
        # template = email_config.template


        msg = EmailMessage()
        msg['Subject'] = email_subject_line #This can be formatted to iterate the subject line based on the send with an f string
        msg['From'] = EMAIL_ADDRESS_FROM
        msg['To'] = email_contact
            
        body = get_template(school, sport)  #These args are for School ONly rn

        # Set the content as HTML
        msg.set_content(body, subtype='html')

        try:
            SMTP_CONN.send_message(msg)

        except smtplib.SMTPConnectError as e:
            print(f'SMTP Connection Error: {e}')
            time.sleep(10)

            SMTP_CONN_2 = SendMail.get_smtp_connection(EMAIL_ADDRESS_FROM, EMAIL_PASS)

            if SMTP_CONN_2:
                SMTP_CONN_2.send_message(msg)
                
        except smtplib.SMTPRecipientsRefused as e:
            # Handle the specific exception
            print(f"Recipient error for {email_contact}: {e}")
        
# -------------------------------------------------------------------------------------------

    #Different logic, output.csv is not created yet. It is at the point of blasting the first 5-. 
    #get next 50 is modified with a try except where the except simply gets the first 50. 
    #Attempts to read from the output.csv everytime   

    def get_next_50(df):

        #email_config does not exist here

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
    

    def process(df, email_config, test=False):

        #next 50 must be passed in as the df, otherwise it will keep running

        EMAIL_ADDRESS_FROM = email_config.EMAIL_ADDRESS_FROM
        EMAIL_PASS = email_config.EMAIL_PASS
        SMTP_CONN = email_config.SMTP_CONN
        contact_column = email_config.contact_column
        sport = email_config.sport
        email_campaign_name = email_config.email_campaign_name
        email_subject_line = email_config.email_subject_line

        #create the test right here with a True False flag. 
        #Then limit it to two. And send to self


        data_list = []
        processed_emails = set()

        if test == True:
            df.loc[0, 'email'] = '2015samtaylor@gmail.com'
            df.loc[1, 'email'] = 'sammytaylor2006@yahoo.com'
            df.loc[2, 'email'] = 'jerrybons2006@gmail.com'
            df = df[:2]
            logging.info('Test argument is True, cutting down frame and sending to personal emails')
            print('Test argument is True, cutting down frame and sending to personal emails')
        else:
            pass


        #Limit df itterrows to test
        for index, row in df.iterrows():

            #Set the time zone to Central Time
            central_time_zone = pytz.timezone('America/Chicago')
            now_central = datetime.now(central_time_zone)
            formatted_date = now_central.strftime("%m/%d/%Y")

            #When running campaigns to non schools try except becomes relevant
            try:
                school = row['HighSchools']
                print(index, school)
            except:
                school = None

            # png_path = row['PNG_PATH']
            email_contact = row[contact_column]
    
            # Check if the email has already been processed
            if email_contact in processed_emails:
                print(f"Skipping email to {email_contact} as it has already been processed.")
                continue

            data = [school, email_contact, sport, formatted_date]
            data_list.append(data)

            # Mark the email as processed
            processed_emails.add(email_contact)
            
            SendMail.send(email_config, email_contact, school)

        
        data_list = pd.DataFrame(data_list, columns=['School', 'Contact', 'Sport', 'Date_Sent'])

        data_list.rename(columns = {'Contact': 'contact_email', 'School': 'school', 'Date_Sent': 'date_sent', 'Sport': 'sport'}, inplace = True)
        data_list['date'] = data_list['date_sent'].astype(str)

        data_list['subject'] = email_subject_line
        data_list['position'] = contact_column
        data_list['from'] = EMAIL_ADDRESS_FROM
        data_list['email_campaign_tag'] = email_campaign_name
        data_list['date'] = now_central.strftime("%Y-%m-%d %H:%M:%S")

        #This is present in case the process breaks it knows where to resume
        data_list.to_csv('output.csv', index=False)

        return(data_list)



class EmailConfig:
    def __init__(self, SMTP_CONN, EMAIL_ADDRESS_FROM, EMAIL_PASS, df, contact_column, sport, email_campaign_name,email_subject_line, server, database, table_name):
     
        self.EMAIL_ADDRESS_FROM = EMAIL_ADDRESS_FROM
        self.EMAIL_PASS = EMAIL_PASS
        
        self.SMTP_CONN = SMTP_CONN
        self.df = df

        self.contact_column = contact_column
        self.sport = sport
        self.email_campaign_name = email_campaign_name
        self.email_subject_line = email_subject_line
        # self.template = template
    
        self.server = server
        self.database = database
        self.table_name = table_name




#General Notes

#Sends 1300 emails in 45 mins
#Limit to 1500 emails per day
#Anything over 2000 the entire account gets locked for 24 hours. 
#Limits to 2000 emails per day
# SMTPDataError: (550, b'5.4.5 Daily user sending limit exceeded. For more information on Gmail\n5.4.5 sending limits go to\n5.4.5  https://support.google.com/a/answer/166852 w4-20020a4ae9e4000000b005914f455774sm848190ooc.34 - gsmtp')







