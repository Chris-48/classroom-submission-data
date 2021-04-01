from sqlite3 import connect
from flask import session
import google.oauth2.credentials

DATABASE = "database.db"


def get_credentials():

    query = """
        SELECT token, token_uri, client_id, refresh_token, client_secret, scopes
        FROM classroom_credentials
        WHERE user_id=?;
    """

    with connect(DATABASE) as db:

        cur = db.execute(query, (session["user_id"],))

        credentials = cur.fetchone()

    if not credentials:
        raise Exception("user id not in the database")
    
    credentials = {
        "token": credentials[0],
        "token_uri": credentials[1],
        "client_id": credentials[2],
        "refresh_token": credentials[3],
        "client_secret": credentials[4],
        "scopes": credentials[5] if credentials[5] is None else credentials[5].split(" ")
    }

    return google.oauth2.credentials.Credentials(**credentials)


def store_credentials(credentials) -> None:

    credentials = (
        credentials.token,
        credentials.refresh_token,
        credentials.token_uri, 
        credentials.client_id, 
        credentials.client_secret, 
        " ".join(credentials.scopes),
        session["user_id"]
    )

    with connect(DATABASE) as db:

        print(session["user_id"])

        exist = db.execute(
            "SELECT 1 FROM classroom_credentials WHERE user_id=?", (session["user_id"],)
        ).fetchone()

        if exist:
            query = """
                UPDATE classroom_credentials
                SET token=?, token_uri=?, client_id=?, refresh_token=?, client_secret=? scopes=?
                WHERE user_id=?
            """
        else:
            query = """
                INSERT INTO classroom_credentials 
                (token, token_uri, client_id, refresh_token, client_secret, scopes, user_id)
                VALUES (?,?,?,?,?,?,?);
            """

        db.execute(query, credentials)
        db.commit()
