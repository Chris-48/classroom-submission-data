# Classroom Submission project

## [Vídeo](https://youtube.com) presenting the project

My cs50x final project is a web application that allow the user to easily get the submission data from a classroom course activity that he/she teaches or administers and export this data to a csv file or to google sheets

## Let's start talking about the app.py file

the `app.py` is the file that should be executed to start the application it contains the configuration and all the routes of the flask application, all the functions in this file are decorated with `@app.route()`.

- `index()` this function just redirect the user to the `/select` route

- `select()` this function render the `select.html` and pass to it all user's courses if the user has already login

- `request_api()` this function return the requested data to the client using AJAX, this function checks if it was given enough data to request the classroom API for the topic activities and return it if it wasn't it will request the classroom API for the course topics

- `submission_data()` this function render `submission_data.html` and pass to it the students submission state of the selected activity after requesting the classroom API

- `export_google_sheets()` this function create a new spread sheet in google sheets, append the students submission state data to it and return the url for the recently created spread sheet if the user has already granted us permission to do so if the user didn't than we will ask him/her for permission

- `google_sheets_oauth2callback()` this function is executed after the user grant us permission to create and modify his/her spread sheets, this function will create the google sheets credentials for the user, store it in `credentials.db` and redirect the user to `/select`

- `login()` this function create an authorization url and redirect the user to this url so that he/she can grant us permission to see his/her classroom data

- `classroom_oauth2callback()` this function is executed after the user grant us permission to see his/her classroom data, this function will create the classroom credentials for the user, store it in `credentials.db` and redirect the user to `/select`

- `logout()` this function revoke the user's classroom and google sheets credentials, delete the user id from the session storage and delete the credentials from `credentials.db`

## Helpers folder 

helpers folders contains two files: `database.py` and `credentials.py` this files contain helper functions to interact with the database and manage the credentials respectively 

- ### database.py
  
  - `get_credentials()` this function takes one argument `servise` that is a string and should be "classroom" or "google_sheets", this function is responsible for getting the user credentials to the servise if it's stored in `credentials.db`
  
  - `store_credentials()` this function is responsible for storing the user `servise` credentials in `credentials.db`, it takes two arguments `servise` that is a string it should be "classroom" or "google_sheets" and `credentials` that is a `google.oauth2.credentials.Credentials` object to be store in `credentials.db`

  - `remove_credentials()` this function is responsible for removing the user `servise` credentials from `credentials.db` it takes one arguments `servise` that is a string it should be "classroom" or "google_sheets"

- ### credentials.py

  - `create_credentials` create the `servise` credentials for the user

  - `create_authorization_url()` create an authorization url that the user should be redirected to grant us authorization according to the `servise`

## Connections  folder

connections folder contains two files: `classroom_connection.py` and `google_sheets_connections.py` this files contain classes to create connections between this web application and google APIs 

- ### classroom_connection.classroom_connection() methods

    - support context manager by implementing `__enter__()` and `__exit__()`

  - `get_user_id()` return the id of the user

  - `get_courses()` return a dictionary with the courses and the corresponding id

  - `get_courses_activities()` return a dictionary with the course activities and the corresponding id

  - `get_course_topics()` return a dictionary with the topics of the course and the corresponding id"

  - `get_activities_from_topic()` return a dictionary with the stundents names and the corresponding id 

  - `get_students()` return a dictionary with the stundents names and the corresponding id

  - `submission_data()` return a dictionary with the stundents names as keys and 'Missing'/'Done' as values acording to the submission state

- ### google_sheets_connection.google_sheets_connection() methods

  - support context manager by implementing `__enter__()` and `__exit__()`

  - `create_spread_sheet()` create a spread sheet and return it's id

  - `append()` append data to the given spread sheet

## Templates folder

the templates folder contains three templates `layout.html`, `select.html` and `submission_data.html`

- TODO

## credentials.db

- ### classroom credentials table


        CREATE TABLE classroom_credentials(
            user_id TEXT,
            token TEXT,
            token_uri TEXT,
            client_id TEXT,
            refresh_token TEXT,
            client_secret TEXT,
            scopes TEXT
        );
        CREATE INDEX user_index_classroom ON classroom_credentials (user_id);


- ### google sheets credentials table


        CREATE TABLE google_sheets_credentials(
            user_id TEXT,
            token TEXT,
            token_uri TEXT,
            client_id TEXT,
            refresh_token TEXT,
            client_secret TEXT,
            scopes TEXT
        );
        CREATE INDEX user_index_google_sheets ON google_sheets_credentials (user_id);