from google.cloud import bigquery, storage
import os
import io  # used for buffer to upload to GCS
import pandas
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages



# Also need to write in event & time triggers via pubsub/stackdriver to initiate reports class
"""Trigger instructions: 1) create a PubSub topic to set as sink for StackDriver export
   2) Setup StackDriver logging export, defining a BQ filter to monitor table create/update
   3) Use the below function to be triggered by above PubSub logs in Cloud Functions"""



class Reports:
    """Triggered by table creation/update in BQ. PubSub topic will listen to StackDriver for the table create/edit."""
    def __init__(self):
        """Set up client connections to GCP"""
        self.bq_client = bigquery.Client(project='cpb100-213205')
        self.storage_client = storage.Client(project='cpb100-213205')
        return

    def bq_df(self, query):
        """Query BQ and store results into a PD Dataframe"""
        query_job = self.bq_client.query(query, project='cpb100-213205')
        df = query_job.to_dataframe()
        return df

    def visuals(self, dataframe, filename):
        """Take our dataframe and make chart visualizations.
           Visualizations will be written to a PDF and saved to GCS"""
        bucket = self.storage_client.bucket('survey413reports')

        # Write pdf charts to GCS
        with PdfPages(filename=filename) as pdf:
            for column in dataframe:
                dataframe[column].value_counts().plot(kind='bar')
                plt.title(column.replace("_", " "))
                pdf.savefig()
                plt.close()
        return


    def email(self, report, contacts):
        """Get the PDF report from GCS and email it out to contacts
           with a report tag == 1"""
        return


if __name__ == '__main__':
    # Test execution
    q1 = "SELECT * FROM esce.AggregateSurvey"
    df1 = Reports().bq_df(query=q1)
    Reports().visuals(dataframe=df1, filename='surveycharts.pdf')
