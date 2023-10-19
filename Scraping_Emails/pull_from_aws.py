# Requires a read of everything and then send. 

table_name = 'gmail_scrape'
dynamodb_client = boto3.client('dynamodb')
    
    
# Perform a scan operation to retrieve all records in the table
response = dynamodb_client.scan(TableName=table_name)

items = response['Items']
clean_items = [{key: value[list(value.keys())[0]] for key, value in item.items()} for item in items]
df = pd.DataFrame(clean_items)
df = df[['subject', 'date', 'reply', 'from', 'to', 'first_message', 'reply_thread', '_id']]



# -----------------------------------------------------------------------function to send email----------------------------

def send_mail():
    
    EMAIL_ADDRESS = 'team@customplanet.com'
    EMAIL_PASS = imap_password_customplanet
    contacts = ['2015samtaylor@gmail.com']
    
    msg = EmailMessage()
    msg['Subject'] = 'Daily Email Campaign Update'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = (contact for contact in contacts)


    body ='''
    Attatched is the daily email campaign data
    '''
    
    msg.set_content(body)
    
    # Convert the DataFrame to a CSV in-memory
    csv_data = df.to_csv(index=False)

    # Create an in-memory file-like object
    csv_stream = io.StringIO(csv_data)

    # Attach the CSV in-memory file to the email
    msg.add_attachment(csv_stream.getvalue(),  subtype='csv', filename='email_campaign.csv')
    

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASS)
        smtp.send_message(msg)
        
send_mail()