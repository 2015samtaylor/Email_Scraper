# Automated Email Campaign

This Python codebase is broken up into 3 parts, Scraping Emails, Sending Emails, and MS-SQL/MySQL operations, Diagram/Blueprints.
The contacts are retrieved from an existing MySQL db, and the email data is sent to a MS-SQL db hosted in AWS. 

**Sending Emails Overview**

This script automates the process of sending customized HTML emails. Once the email contacts are available they are passed through a loop which utilizes an SMTP connection, and passes in the template for each email.
There is an available option within all emails to opt out of future email campaigns.

-----------------------------------------------------------------------------

**Scraping Emails Overview**

This script automates the extraction and organization of email responses for storage in a MS-SQL database. Here's a brief overview:

The parameters for scraping are subject line, and start date. These two are taken into account within the SMTP connection to search the inbox and outbox for given email data. Once data has been queried, it is separated into 3 sections, inbox, outbox, and thread. 
Thread pairs any responses from sent messages, and uses (NLP) natural language processing to assess if feedback was positive or negative. 

All new emails sent, received are accounted for in the MS-SQL db. 


Any emails sent out which get sent back due to a defective email are logged to the DB as unsubscribed. The process checks through all distinct subject lines in order to be up to date. 





- 

