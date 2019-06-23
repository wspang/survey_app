from GCP import DSSurvey, Deployment

"""********************************************************************************************************************
                                            Create the Survey in DataStore via CSV Upload
                                            Email a Link of Survey to All Contacts
********************************************************************************************************************"""


def setup():
    # Make the survey in DataStore
    DSSurvey().make(path="/users/will/downloads/csvsurvey.csv")

    # Get a list of Contacts from DataStore query. Contains employee IDs, email addresses, and phone numbers in dict form
    contacts = Deployment().contacts()
    # Loop through Contacts and Deploy Emails containing the survey link, and SMS containing survey
    for contact in contacts:
        # Deploy email
        Deployment().email(receiver=contact['emailAddress'], receiver_name=contact['fullName'])
        # Send SMS //still in progress
    return


# Execute then print a success message.
setup()

print("Survey has successfully uploaded.\nEmails have deployed.")