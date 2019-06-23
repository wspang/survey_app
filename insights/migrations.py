"""This file executes a series of command line arguments.
   The arguments will export survey data from DataStore to GCS.
   Then, BigQuery will read the GCS metadata into a new table."""


import os
from datetime import datetime, timedelta


class Migration:
    def __init__(self):
        """Kind will be referenced as previous day survey. Will carry over as naming convention."""
        self.YESTERDAY = datetime.utcnow() # - timedelta(1)
        self.KIND = "{0}survey".format(self.YESTERDAY.strftime('%m%d%y'))
        return

    def export(self):
        """Export datastore survey data for previous day into GCS metadata"""
        ds_gcs = "gcloud datastore export --kinds='{0}' --namespaces='(default)' gs://dsdump".format(self.KIND)
        # Execute command with os.system
        os.system(ds_gcs)
        return

    def upload(self):
        """Upload GCS metadata into BQ staging table. Data to be cleaned and appended to actual survey table."""
        # Get the directory of the datastore export just made.
        outputUrlPrefix = str(input("Paste the outputUrlPrefix received above."))
        # Find DataStore export metadata and feed into BQ table called {survey date}survey
        gcs_bq = ("bq --location=US load --source_format=DATASTORE_BACKUP --replace esce.staging " 
                  "{1}/default_namespace/kind_{0}/default_namespace_kind_{0}.export_metadata".format(
                    self.KIND, outputUrlPrefix))
        # Execute with command line
        os.system(gcs_bq)
        return

    def append(self):
        """Parse the data in table and append to master table -- which is partitioned by survey date!"""
        destination_table = "AggregateSurvey"
        query = "'SELECT * EXCEPT (__key__, __error__, __has_error__) from `esce.staging`'"
        bq_append = ("bq --location=US query --destination_table "
                     "cpb100-213205:esce.{0} --append --use_legacy_sql=false {1}".format(destination_table, query))
        os.system(bq_append)
        return


"""Query column names"""
# Get column names
# SELECT column_name
# FROM esce.INFORMATION_SCHEMA.COLUMNS
# WHERE table_name="april"; #and column_name like '[A-Z]%';


# 4) Delete the metadata BigQuery table


"""********************************************************************************************************************
                                            EXECUTE MIGRATIONS
********************************************************************************************************************"""

if __name__ == '__main__':
    Migration().export()
    print("Data export from DataStore to GCS is successful.")
    Migration().upload()
    print("Data upload from GCS to BQ staging table is successful.")
    Migration().append()
    print("Data has been cleaned and appended to master table.\nData migration is successful")
