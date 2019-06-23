"""This file is used to submit a csv file of contacts up to DataStore"""

from GCP import Contacts
Contacts("Tredence").upload(str(input("Please enter path to contacts file\n")))
print("Contacts successfully uploaded.")