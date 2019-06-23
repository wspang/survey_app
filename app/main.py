from flask import Flask, render_template, redirect
import logging
from GCP import DSSurvey, Deployment


"""********************************************************************************************************************
                                            WebApp Section of ESCE app
********************************************************************************************************************"""
app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    """Get survey Q & A from DataStore and render as main page survey."""
    survey_qa = DSSurvey().survey()
    logging.info("User opened survey.")
    # //use a KV for display and record on main. Need to switch to {{question}}, {{answer[2]}} !! is index 1 | 2?
    return render_template('main.html', questions=survey_qa, surveyName="4/18 Demo")


@app.route('/survey', methods=['POST'])
def survey():
    """Record responses in DataStore and thank for submission"""
    DSSurvey().responses()
    logging.info("User submitted survey.")
    return render_template('submitted.html')


@app.route('/upload/contacts/<company>', methods=['POST'])
def upload(company):
    """Find a csv file in GCS containing contacts. Upload that data to Datastore.
       This is solely meant to be an API, not interace for app."""
    Deployment(company).upload()

@app.errorhandler(500)
def server_error(e):
    logging.exception("An error occured during a request.")
    return """An internal error occured: <pre>{}</pre>
    See logs for full stacktrace.""".format(e), 500


if __name__ == '__main__':
    # Use to run locally
    # app.yaml is used when running on GCP App Engine
    app.run(host='127.0.0.1', port=8080, debug=True)
