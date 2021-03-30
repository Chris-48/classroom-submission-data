from flask import render_template
from flask import Flask
from flask import request
from flask import redirect
from flask import session
from flask.helpers import url_for

import os
from requests import post

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from helpers import credentials_to_dict
from connections.classroom_connection import classroom_connection

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.secret_key = "secret"

CLIENT_SECRETS = {
    "web": {
        "client_id": os.environ["CLIENT_ID"],
        "project_id": os.environ["PROJECT_ID"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.environ["CLIENT_SECRET"]
    }
}

SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.topics.readonly",
    "https://www.googleapis.com/auth/classroom.student-submissions.students.readonly",
    "https://www.googleapis.com/auth/classroom.rosters.readonly"
]


@app.route("/")
def index():
    return redirect("/select")


@app.route("/select")
def select():
    courses = None

    if "credentials" in session:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])

        with classroom_connection(credentials) as classroom:
            courses = classroom.get_courses()

    return render_template("select.html", courses=courses)


@app.route("/request_api", methods=["POST"])
def request_api():

    course_id = request.form.get("course_id")
    topic_id = request.form.get("topic_id")

    credentials = google.oauth2.credentials.Credentials(**session['credentials'])

    if course_id:
        with classroom_connection(credentials) as classroom:
            if topic_id:
                return classroom.get_activities_from_topic(course_id, topic_id)

            return classroom.get_courses_topics(course_id)
    else:
        return "wrong request", 406



@app.route("/submission_data", methods=["POST"])
def submission_data():
    
    course_id = request.form.get("course_id")
    activity_id = request.form.get("activity_id")

    credentials = google.oauth2.credentials.Credentials(**session['credentials'])    

    with classroom_connection(credentials) as classroom:
        students = classroom.get_students(course_id)

        students_submission_states = classroom.submission_data(course_id, activity_id, students)
    print(students_submission_states)
    return render_template("submission_data.html", students_submission_states=students_submission_states)


@app.route("/login")
def login():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_config(CLIENT_SECRETS, scopes=SCOPES)

    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    session['state'] = state

    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        CLIENT_SECRETS, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('select'))


@app.route("/logout")
def logout():
    if 'credentials' in session:
   
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])

        revoke = post('https://oauth2.googleapis.com/revoke',
        params={'token': credentials.token},
        headers = {'content-type': 'application/x-www-form-urlencoded'})

        del session["credentials"]

        return redirect("/")


if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    app.run('localhost', 5000, debug=True)