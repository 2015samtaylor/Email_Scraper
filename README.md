# Email Scraper and DB Update (MS-SQL)

This Python codebase is broken up into 3 parts, Scraping Emails, Sending Emails, and MS-SQL Diagram/Blueprints

**Sending Emails Documentation**

This script automates the process of sending personalized emails to a list of contacts for an email campaign. Here's a concise overview:

1. **Imports:**
   - Essential libraries and modules are imported, including `pandas` for data handling, `numpy` for numerical operations, and custom modules for database operations and email sending.

2. **Data Preparation:**
   - Reads a CSV file containing information about schools, contacts, and email paths.
   - Temporarily modifies email addresses for testing purposes.

3. **Email Sending Process:**
   - Iterates through the rows of the dataset.
   - Creates a unique identifier for each email using the UUID library.
   - Checks if an email address has already been processed to avoid duplication.
   - Gathers data for database storage and sends personalized emails using the `send_mail` function.
   - Generates a DataFrame with campaign details to create an initial baseline, and record what emails have been sent to who

4. **Database Connection:**
   - Specifies the database connection details for the SQL database.

5. **Database Interaction:**
   - Creates a `DatabaseConnector` instance with the specified connection details.
   - Sends the email campaign data to the 'email_history' table using the `send` method.

This script streamlines the process of conducting email campaigns, facilitating efficient tracking and management of sent emails in a SQL database.

-----------------------------------------------------------------------------

**Scraping Emails Documentation**

This script automates the extraction and organization of email responses for storage in a SQL database. Here's a brief overview:

1. **Imports:**
   - Essential libraries and modules are imported, including `logging` for file-based logging, `pandas` for data handling, and custom modules for scraping and database operations.

2. **Logging Configuration:**
   - Configures logging to capture timestamped log messages in "Email_Scraper.log."

3. **Main Function - `process`:**
   - Takes parameters for the subject line, email address, and password.
   - Scrapes inbox and outbox messages related to the specified subject.
   - Processes and cleanses the data, combining it into a formatted dataframe.
   - Specifies database connection details and creates a `DatabaseConnector` instance.
   - Appends new records to the database and updates the 'reply_thread' column.
   - Returns dataframes: `inbox`, `outbox`, `thread`, and `new_records`.

4. **Function Execution:**
   - Executes the `process` function with specific parameters and stores returned dataframes.



- 

