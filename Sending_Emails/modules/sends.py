import smtplib
from email.message import EmailMessage
# import imghdr
import base64
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

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS_FROM, EMAIL_PASS)
            smtp.send_message(msg)

