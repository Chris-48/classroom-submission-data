# Standard imports
import os
from requests import post

# Flask imports
from flask import render_template, Flask, request, redirect, session

# Local imports
from helpers.credentials import create_authorization_url, create_credentials
from helpers.database import get_credentials, remove_credentials, store_credentials

from connections.classroom_connection import classroom_connection
from connections.google_sheets_connection import google_sheets_connection

# Configure application
app = Flask(__name__)

# Auto reload the templates
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Set the secret key
app.secret_key = "secret"

# OAuth 2 client id for google classroom api
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

# The user need to grant us authorization to see
    # the user courses,
    # the topics from the courses,
    # the students from the courses,
    # and the students submissions.
CLASSROOM_SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.topics.readonly",
    "https://www.googleapis.com/auth/classroom.student-submissions.students.readonly",
    "https://www.googleapis.com/auth/classroom.rosters.readonly"
]

# OAuth 2 client id for google google sheets api
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

# The user need to grant us authorization to create and modify spread sheets
GOOGLE_SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

@app.route("/")
def index():
    """ Main route redirect to /select """
    
    return redirect("/select")


@app.route("/select")
def select():
    """ Load the select template so the user can select the course topic and activity to get the data from """

    courses = None

    # If the use have already granted authorization get the user's courses
    if "user_id" in session:

        with classroom_connection(get_credentials("classroom")) as classroom:
            courses = classroom.get_courses()

    # render select.html
    return render_template("select.html", courses=courses)


@app.route("/request_api", methods=["POST"])
def request_api():
    """ Use AJAX. Get the requested info by requesting the classroom API """

    # Get from the request the course id and the topic id, they might not exist
    course_id = request.form.get("course_id")
    topic_id = request.form.get("topic_id")

    if course_id:
        
        with classroom_connection(get_credentials("classroom")) as classroom:
            
            # If the topic id was given in the request return the activities from this topic
            if topic_id:
                return classroom.get_activities_from_topic(course_id, topic_id)
            # Else return the course's topics
            return classroom.get_course_topics(course_id)
    else:
        # Return 406 if wasn't course id given in the request
        return "bad request", 406


@app.route("/submission_data", methods=["POST"])
def submission_data():
    """ 
    Load the submission data template so the user can see the submission state from the students
    and export the data to csv or to google sheets 
    """

    # Get the course id from the request
    course_id = request.form.get("course_id")

    # Get the activity id and title
    activity_id, activity_title = request.form.get("activity").split("---")

    # Get the students submission state
    with classroom_connection(get_credentials("classroom")) as classroom:
        students = classroom.get_students(course_id)

        students_submission_states = classroom.submission_data(course_id, activity_id, students)

    # Render submission_data.html gives it the students submission state and title from the activity
    return render_template(
        "submission_data.html",
        students_submission_states=students_submission_states,
        activity_title=activity_title
    )


@app.route("/export_google_sheets", methods=["POST"])
def export_google_sheets():
    """ Use AJAX. Export the students submission state data to google sheets """

    # Get google sheets credentials from the database
    credentials = get_credentials("google_sheets")

    # If the google sheets credentials exist in the database
    if credentials:

        with google_sheets_connection(credentials) as google_sheets:
            
            # Create a new spread sheet
            spread_sheet_id, spread_sheet_url = google_sheets.create_spread_sheet(
                request.form.get("activity_title")
            )

            # Append the data to the recently created spread sheet
            google_sheets.append(request.form, spread_sheet_id=spread_sheet_id)

        # Return the url for the recently created spread sheet
        return spread_sheet_url
    
    # Else ask the user for authorization
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
    """ 
    The route that the user will be send after grant permission to
    create and modify his/her spread sheets 
    """

    # Create the credentials for the google sheets
    credentials = create_credentials(
        "google_sheets",
        GOOGLE_SHEETS_CLIENT_SECRETS, 
        GOOGLE_SHEETS_SCOPES, 
        session["google_sheets_state"], 
        request.url
    )

    # Store the user google sheets credentials in the database
    store_credentials("google_sheets", credentials)

    # Go back to the /select route
    return redirect("/select")


@app.route("/login")
def login():
    """ Ask the user for authorization """

    # Create the authorization url 
    authorization_url, state = create_authorization_url(
        "classroom",
        CLASSROOM_CLIENT_SECRETS,
        CLASSROOM_SCOPES
    )

    session["classroom_state"] = state

    return redirect(authorization_url)


@app.route("/classroom_oauth2callback")
def classroom_oauth2callback():
    """ The route that the user will be send after grant permission to see his/her classroom info """

    # Create the credentials for the google classroom 
    credentials = create_credentials(
        "classroom",
        CLASSROOM_CLIENT_SECRETS,
        CLASSROOM_SCOPES,
        session["classroom_state"],
        request.url
    )

    # Store the user id
    with classroom_connection(credentials) as classroom:
        session["user_id"] = classroom.get_user_id()

    # Store the credentials in the database
    store_credentials("classroom", credentials)

    # Go back to the /select route
    return redirect("/select")


@app.route("/logout")
def logout():
    """ Logout """

    # Revoke the credentials
    if "user_id" in session:
        
        classroom_credentials = get_credentials("classroom")

        if classroom_credentials:
            
            # Revoke the classroom token
            post(
                "https://oauth2.googleapis.com/revoke",
                params={"token": classroom_credentials.token},
                headers={"content-type": "application/x-www-form-urlencoded"}
            )

            # Remove the classroom credentials to from the database
            remove_credentials("classroom")

        google_sheets_credentials = get_credentials("google_sheets")

        if google_sheets_credentials:
            
            # Revoke the google sheets token
            post(
                "https://oauth2.googleapis.com/revoke",
                params={"token": google_sheets_credentials.token},
                headers={"content-type": "application/x-www-form-urlencoded"}
            )

            # Remove the google sheets credentials to from the database
            remove_credentials("google_sheets")

        # Remove the user id from the session cookies
        del session["user_id"]

    # Go back to the main route
    return redirect("/")


if __name__ == "__main__":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    app.run("localhost", 5000, debug=True)
