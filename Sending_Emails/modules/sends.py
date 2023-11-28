import smtplib
from email.message import EmailMessage
import imghdr
from datetime import datetime
contacts = ['2015samtaylor@gmail.com']


class send:

    def send_mail(EMAIL_ADDRESS_FROM, EMAIL_PASS, school, sport, png_path, email, unique_identifier):
        
        msg = EmailMessage()
        msg['Subject'] = f'Local {sport} Jerseys for {school}'
        msg['From'] = EMAIL_ADDRESS_FROM
        # msg['To'] = (contact for contact in contacts)
        msg['To'] = email

        #Create the body of the email by setting the content

        body = f'''
                <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 0;
                    }}

                    .container {{
                        background-color: #ffffff;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}

                    h1 {{
                        color: #007BFF;
                    }}

                    p {{
                        font-size: 16px;
                        line-height: 1.6;
                    }}

                    a {{
                        color: #007BFF;
                        text-decoration: none;
                    }}

                    a:hover {{
                        text-decoration: underline;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Hello {school}!</h1>
                    <p>We are a local supplier for Custom {sport} Jerseys. How would you like to check out what we have?</p>
                    <p>We can put your logo on just about anything!</p>
                    <p>Check out our website or give us a call to get a free sample at <a href="http://customplanet.com">customplanet.com</a>.</p>
                    <!--Hidden UUID: {unique_identifier}-->
                </div>
            </body>
            </html>
        '''
        
        #subtype must be indicated if it is HTML
        msg.set_content(body, subtype='html')
        
        #insert School logos into the Email thread from the PNG folder
        try:
            with open(f'PNGs/{png_path}.png', 'rb') as f:
                file_data = f.read()
                file_type = imghdr.what(f.name)
                file_name = f.name
                msg.add_attachment(file_data, maintype = 'image', subtype = file_type, filename = file_name)

        except FileNotFoundError:
            pass


        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS_FROM, EMAIL_PASS)
            smtp.send_message(msg)