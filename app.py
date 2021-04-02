import os
import json
from requests import post
from sqlite3 import connect

from flask import render_template
from flask import Flask
from flask import request
from flask import redirect
from flask import session

from helpers import store_credentials
from helpers import get_credentials
from helpers import create_credentials
from helpers import create_authorization_url, remove_credentials

from connections.classroom_connection import classroom_connection
from connections.google_sheets_connection import google_sheets_connection

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.secret_key = "secret"

CLASSROOM_CLIENT_SECRETS = {
    "web": {
        "client_id": os.environ["CLASSROOM_CLIENT_ID"],
        "project_id": "classroom-data-308900",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.environ["CLASSROOM_CLIENT_SECRET"]
    }
}

GOOGLE_SHEETS_CLIENT_SECRETS = {
    "web": {
        "client_id": os.environ["GOOGLE_SHEETS_CLIENT_ID"],
        "project_id": "classroom-data-308900",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.environ["GOOGLE_SHEETS_CLIENT_SECRET"]
    }
}

CLASSROOM_SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.topics.readonly",
    "https://www.googleapis.com/auth/classroom.student-submissions.students.readonly",
    "https://www.googleapis.com/auth/classroom.rosters.readonly"
]

GOOGLE_SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

@app.route("/")
def index():
    return redirect("/select")


@app.route("/select")
def select():
    courses = None

    if "user_id" in session:

        with classroom_connection(get_credentials("classroom")) as classroom:
            courses = classroom.get_courses()

    return render_template("select.html", courses=courses)


@app.route("/request_api", methods=["POST"])
def request_api():

    course_id = request.form.get("course_id")
    topic_id = request.form.get("topic_id")

    if course_id:
        with classroom_connection(get_credentials("classroom")) as classroom:
            if topic_id:
                return classroom.get_activities_from_topic(course_id, topic_id)

            return classroom.get_courses_topics(course_id)
    else:
        return "bad request", 406


@app.route("/submission_data", methods=["POST"])
def submission_data():

    course_id = request.form.get("course_id")
    activity_id, activity_title = request.form.get("activity").split("---")

    with classroom_connection(get_credentials("classroom")) as classroom:
        students = classroom.get_students(course_id)

        students_submission_states = classroom.submission_data(course_id, activity_id, students)

    return render_template(
        "submission_data.html",
        students_submission_states=students_submission_states,
        activity_title=activity_title
    )


@app.route("/export_google_sheets", methods=["POST"])
def export_google_sheets():
    
    credentials = get_credentials("google_sheets")

    if credentials:

        with google_sheets_connection(credentials) as google_sheets:
            
            spread_sheet_id, spread_sheet_url = google_sheets.create_spread_sheet(
                request.form.get("activity_title")
            )

            google_sheets.append(request.form, spread_sheet_id=spread_sheet_id)

        return spread_sheet_url
    else:

        authorization_url, state = create_authorization_url(
            "google_sheets",
            GOOGLE_SHEETS_CLIENT_SECRETS, 
            GOOGLE_SHEETS_SCOPES
        )

        session["google_sheets_state"] = state

        return authorization_url


@app.route("/google_sheets_oauth2callback")
def google_sheets_oauth2callback():

    credentials = create_credentials(
        "google_sheets",
        GOOGLE_SHEETS_CLIENT_SECRETS, 
        GOOGLE_SHEETS_SCOPES, 
        session["google_sheets_state"], 
        request.url
    )

    store_credentials("google_sheets", credentials)

    return redirect("/select")


@app.route("/login")
def login():
    
    authorization_url, state = create_authorization_url(
        "classroom",
        CLASSROOM_CLIENT_SECRETS,
        CLASSROOM_SCOPES
    )

    session["classroom_state"] = state

    return redirect(authorization_url)


@app.route("/classroom_oauth2callback")
def classroom_oauth2callback():

    credentials = create_credentials(
        "classroom",
        CLASSROOM_CLIENT_SECRETS,
        CLASSROOM_SCOPES,
        session["classroom_state"],
        request.url
    )

    with classroom_connection(credentials) as classroom:
        session["user_id"] = classroom.get_user_id()

    store_credentials("classroom", credentials)

    return redirect("/select")


@app.route("/logout")
def logout():

    if "user_id" in session:
        
        classroom_credentials = get_credentials("classroom")

        if classroom_credentials:
            post(
                "https://oauth2.googleapis.com/revoke",
                params={"token": classroom_credentials.token},
                headers={"content-type": "application/x-www-form-urlencoded"}
            )

            remove_credentials("classroom")

        google_sheets_credentials = get_credentials("google_sheets")

        if google_sheets_credentials:

            post(
                "https://oauth2.googleapis.com/revoke",
                params={"token": google_sheets_credentials.token},
                headers={"content-type": "application/x-www-form-urlencoded"}
            )

            remove_credentials("google_sheets")

        del session["user_id"]

    return redirect("/")


if __name__ == "__main__":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    app.run("localhost", 5000, debug=True)

    session.clear()
