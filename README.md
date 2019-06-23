# survey_app
Code for Survey App and Data Processing Processes. Used to conduct employee surveys.
# How it Works
An employer can upload a CSV survey with question and possible answers. The app will parse the information and store the survey in NoSQL DataStore.
Contacts are also stored in DataStore. When uploaded, an email is sent out to every employee in the Contact Kind with a link to a webpage for filling out the survey.
Responses are recorded in DataStore as well. At the end of the day, a DataStore export is performed to transfer the data to a GCS Bucket.
From the GCS Bucket, the data is loaded into a BigQuery `truncated` staging table, where a cleansing query is performed to remove DataStore metadata and append survey results to a master table.
DataStore exports require a dump into GCS as a direct transfer to BigQuery is not possible (unless doing a query to DF).
When results are uploaded to the BigQuery Table, this creates a log in StackDriver that PubSub is listening to. Seeing this specific log triggers a Cloud Function.
The Cloud Function queries that survey data, creates a bar chart to visualize proportion of answers for every question, and saves every graph in a multi-page PDF file.
The PDF file is then stored in a GCS Bucket. Currently working on automating an email deployment of report to every contact in DataStore with a `manager` flag on contact entity.
