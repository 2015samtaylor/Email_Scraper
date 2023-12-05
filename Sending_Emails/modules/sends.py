import smtplib
from email.message import EmailMessage
import imghdr
import base64


class SendMail:

    def send(EMAIL_ADDRESS_FROM, EMAIL_PASS, global_subject_line, school, sport, png_path, email, unique_identifier):
        msg = EmailMessage()
        msg['Subject'] = global_subject_line.format(sport, school)
        msg['From'] = EMAIL_ADDRESS_FROM
        msg['To'] = email

        # Read the PNG file as binary data and encode it as base64
        png_file_path = f'PNGs/{png_path}.png'
        try:
            with open(png_file_path, 'rb') as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
        except FileNotFoundError:
            image_base64 = ''

        # Create the body of the email by setting the content
        body = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body{{
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

                    a, .underline:hover {{
                        color: #007BFF;
                        text-decoration: none;
                    }}

                    a:hover, .underline:hover {{
                        text-decoration: underline;
                    }}

                    .image-container {{
                        display: flex;
                        justify-content: space-between;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Hello {school}]!</h1>
                    <p>We are excited to introduce ourselves as your local supplier for <span class="underline">Custom Sports Jerseys and apparel</span>. Elevate your team's spirit with our high-quality, personalized jerseys designed to make a statement on the field.</p>
                    <p>Why choose us?</p>
                    <ul>
                        <li>Custom Designs: Bring your unique vision to life with our customizable design options.</li>
                        <li>Quality Materials: Our jerseys are crafted from premium materials for comfort and durability.</li>
                        <li>Quick Turnaround: Fast and efficient service to meet your tight schedules.</li>
                    </ul>
                    <p>Ready to get started?</p>
                    <p>Visit our website or give us a call to request a free sample and explore our catalog: <a href="http://customplanet.com" class="underline">customplanet.com</a>.</p>
                    <input type="hidden" id="hidden-uuid" value="{unique_identifier}">
                     <div class="image-container">
                        <img src="https://lh3.googleusercontent.com/p/AF1QipMOx-lGQC-IlQwU0kBo5uP18BkuLrDoKAKGDS9h=s1360-w1360-h1020" alt="Customplanet Culture 1" width="300px">
                        <img src="https://lh3.googleusercontent.com/p/AF1QipNLF0i0wl_6Y4VF9vHJKpjGtMHhgT70_ADLww8j=s1360-w1360-h1020" alt="Customplanet Culture 2" width="300px">
                    </div>
                    <p class="footer">Best Regards,<br>Your Team at Customplanet</p>
                    <p class="sport-reference">{sport} season is nearly here!</p>
                    <p>For inquiries, contact us at: <a href="(801) 810-8337" class="underline"> (801) 810-8337</a></p>
                </div>
            </body>
            </html>
        '''

        # Set the content as HTML
        msg.set_content(body, subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS_FROM, EMAIL_PASS)
            smtp.send_message(msg)
