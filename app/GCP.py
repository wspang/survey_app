"""This file holds all the functions for executing the app"""

from google.cloud import datastore
from datetime import datetime
from flask import request
import json
import yagmail
import csv


class DSSurvey:
    """This class is for creating the survey and collecting responses in main.py file.
       'surveys' Kind in Datastore is for holding the survey templates, which are keyed by their
       survey date. Survey responses are stored in a distinct kind for that survey date."""
    # Datastore structure for survey creation is question, report, a1-a`n`

    def __init__(self):
        self.datastore_client = datastore.Client()
        self.kind = f"{datetime.utcnow().strftime('%m%d%y')}survey"
        self.sourcekind = "surveys"
        return

    def make(self, path):
        """Read a csv file to make the survey key in DataStore. Surveys are stored in 'surveys' kind."""

        # 1) Read a csv file and create a DataStore entity for the survey template.
        key = self.datastore_client.key(self.sourcekind, datetime.utcnow().strftime('%m%d%y'))
        entity = datastore.Entity(key)
        charts = []  # structured list to get chart types to make for each question

        # Read the CSV survey and have element names as the question and an array of possible answers as values
        # CSV format will be [0] question and [1:] answers
        data = csv.DictReader(open(path))
        for row in data:
            charts.append(row['chart'])
            del row['chart']
            q = row['question']  # This will be a series of Q&A to make up the Survey
            del row['question']
            answers = [v for v in row.values() if v != ""]
            entity[q] = answers
        entity['charts'] = charts
        # Save the submissions to Datastore
        self.datastore_client.put(entity=entity)
        return

    def survey(self):
        """Get the initial survey for webpage from Datastore.
        Jsonify for html to parse on main webpage.
        Set kind to survey date and key to survey Q & A prompt"""
        # The key for the survey Q & A will always be 9999
        survey_source = self.datastore_client.key(self.sourcekind, datetime.utcnow().strftime('%m%d%y'))
        survey = dict(self.datastore_client.get(survey_source))
        return survey

    def responses(self):
        """Write the responses back to DataStore survey for that date. Key is Employee ID
           that is submitted on webpage to avoid employees answering multiple times.
           This method is called after an employee submits their answers."""

        empid = request.form.get('empid')
        key = self.datastore_client.key(self.kind, empid)
        entity = datastore.Entity(key)

        # Loop through answers in survey form and record to DataStore for given question.
        for q in DSSurvey().survey().keys():
            a = request.form[q]
            entity[q] = a
        # Non radio question below will take in the separate class of text input.
        entity['Any other feedback'] = request.form.get('closing')
        # Save the submissions to Datastore
        self.datastore_client.put(entity=entity)
        return


class Deployment:
    """Used to deploy the webapp to contacts in DB. Currently supports Email but also looking
       to expand to SMS via Twilio or Nexmo."""

    def __init__(self, company):
        self.datastore_client = datastore.Client()
        self.kind = "{0}Employees".format(company)
        self.url = "https://cpb100-213205.ESCE.appspot.com"
        return

    def upload(self, path):
        """Given a csv file, upload contacts for that company"""
        data = csv.DictReader(open(path))
        for row in data:
            key = self.datastore_client.key(self.kind, row['empid'])
            entity = datastore.Entity(key)

            entity['admin'] = row['admin']
            entity['emailAddress'] = row['emailAddress']
            entity['fullName'] = row['fullName']
            entity['phoneNumber'] = row['phoneNumber']
            entity['report'] = row['report']
            # Save the submissions to Datastore
            self.datastore_client.put(entity=entity)
        return

    def contacts(self):
        """Query DataStore to retrieve all employee ids, emails, and phone numbers from employee contact kind"""
        query = self.datastore_client.query(kind=self.kind)
        employees = query.fetch()
        # Return a list of dictionaries where each iterator is of keys[employee id, emailaddress, phone #]
        contacts = []
        for i in employees:
            employee = dict(i)
            employee['empid'] = str(i.key)[str(i.key).find('0'): str(i.key).find('0') + 4]
            contacts.append(employee)
        return contacts

    def email(self, receiver, receiver_name):
        """Utilize yagmail to deploy emails to everyone in contact list with survey link"""
        deployer = "survey-project@gmail.com"
        passw = "password"
        yagmail.register(username=deployer, password=passw)
        yag = yagmail.SMTP(deployer)
        yag.send(
            to=receiver,
            subject="Employee Survey",
            contents="Yo {0}?\nPlease follow the following link to take survey:\n{1}".format(receiver_name, self.url))
        return
