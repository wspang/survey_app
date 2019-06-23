from google.cloud import bigquery, storage, datastore
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class Reports:
    """Triggered by table creation/update in BQ. PubSub topic will listen to StackDriver for the table create/edit."""
    def __init__(self):
        """Set up client connections to GCP"""
        self.bq_client = bigquery.Client()
        self.storage_client = storage.Client()
        self.datastore_client = datastore.Client()
        return

    def bq_df(self, query):
        """Query BQ and store results into a PD Dataframe"""
        query_job = self.bq_client.query(query)
        df = query_job.to_dataframe()
        return df

    def visuals(self, dataframe, filename):
        """Take our dataframe and make chart visualizations. Specified as survey['Q'][0] from user submission.
           Visualizations will be written to a PDF"""
        # Need to query DataStore chart type element, more efficient
        query = self.datastore_client.query(kind='survey')
        query.add_filter('name', '=', f"surveys{datetime.utcnow().strftime('%m%d%y')}")
        charts = query.fetch()['charts']  # Returns an array of charts to use per column
        # Include a counter to iterate through chart list
        n = 0
        # Write pdf charts to GCS
        with PdfPages(filename=f"/tmp/{filename}") as pdf:
            for column in dataframe:
                # Create the chart per column
                dataframe[column].value_counts().plot(kind=charts[n])  # Chart type, i.e bar, pie, line,, etc.
                plt.title(column.replace("_", " "))
                pdf.savefig()
                plt.close()
                n += 1  # move onto next chart in list

        """Take the report pdf from tmp storage and move it to GCS bucket"""
        bucket = self.storage_client.bucket('survey413reports')
        blob = bucket.blob('surveyreport.pdf')
        blob.upload_from_filename(filename=f"/tmp/{filename}", content_type='application/pdf')
        return

    def email(self, data, context):
        """Emails the report written to GCS to all DS contacts with report == 1"""
        kind = "Employees"
        # Create a list of recipients from a DataStore query to get the report email
        query = self.datastore_client.query(kind=kind)
        query.add_filter('report', '=', True)
        recipients = query.fetch()  # filter for element value == 1

        # Get the pdf file from GCS
        bucket = self.storage_client.get_bucket(data['bucket'])
        blob = bucket.get_blob(data['name'])
        pdf_report = blob.download_as_string()
        pdf = MIMEApplication(pdf_report)

        # Set up email server
        host = "smtp.gmail.com"
        port = 587
        sender = "surveys@gmail.com"
        passw = "password"
        # App password: mymj glhe lcao vweo      // received key from setting up gmail

        # Set up email message
        msg = MIMEMultipart()
        msg.attach(pdf)
        emailmessage = MIMEText("PFA the survey report.\nThanks,\nESCE", 'plain', 'utf-8')
        msg.attach(emailmessage)

        # Send the message
        mailer = smtplib.SMTP(host=host, port=port)
        mailer.login(user=sender, password=passw)
        mailer.connect()
        mailer.sendmail(from_addr=sender, to_addrs='willjspangler@gmail.com',  msg.as_string())
        mailer.close()

        return


def cloudfunction_report(data, context):
    # Execute flow of the above class to get reports to GCS     // embedded in Cloud Function.
    report = 'surveycharts.pdf'
    q1 = "SELECT * FROM esce.AggregateSurvey"
    df1 = Reports().bq_df(query=q1)
    Reports().visuals(dataframe=df1, filename=report)
    return
Reports().email()