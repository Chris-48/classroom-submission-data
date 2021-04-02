from sqlite3 import connect
from flask import session
import google.oauth2.credentials
import google_auth_oauthlib
from flask.helpers import url_for


DATABASE = "database.db"


def get_credentials(servise: str):

    query = f"""
        SELECT token, token_uri, client_id, refresh_token, client_secret, scopes
        FROM {servise}_credentials
        WHERE user_id=?;
    """

    with connect(DATABASE) as db:
        credentials = db.execute(query, (session["user_id"],)).fetchone()

    if not credentials:
        return

    credentials = {
        "token": credentials[0],
        "token_uri": credentials[1],
        "client_id": credentials[2],
        "refresh_token": credentials[3],
        "client_secret": credentials[4],
        "scopes": credentials[5] if credentials[5] is None else credentials[5].split(" ")
    }

    return google.oauth2.credentials.Credentials(**credentials)


def store_credentials(servise: str, credentials) -> None:

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

        exist = db.execute(
            f"SELECT 1 FROM {servise}_credentials WHERE user_id=?", (session["user_id"],)
        ).fetchone()

        if exist:
            query = f"""
                UPDATE {servise}_credentials
                SET token=?, token_uri=?, client_id=?, refresh_token=?, client_secret=?, scopes=?
                WHERE user_id=?;
            """
        else:
            query = f"""
                INSERT INTO {servise}_credentials 
                (token, token_uri, client_id, refresh_token, client_secret, scopes, user_id)
                VALUES (?,?,?,?,?,?,?);
            """

        db.execute(query, credentials)
        db.commit()


def remove_credentials(service: str):
    
    with connect(DATABASE) as db:
        
        db.execute(
            f"DELETE FROM {service}_credentials WHERE user_id=?;", 
            (session["user_id"],)
        )
        db.commit()


def create_credentials(service: str, client_secret, scopes, state, url):
    
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_secret,
        scopes=scopes,
        state=state
    )

    flow.redirect_uri = url_for(f"{service}_oauth2callback", _external=True)

    authorization_response = url
    flow.fetch_token(authorization_response=authorization_response)

    return flow.credentials


def create_authorization_url(service: str, client_secret, scopes):

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_secret,
        scopes=scopes
    )

    flow.redirect_uri = url_for(f"{service}_oauth2callback", _external=True)

    return flow.authorization_url(access_type="offline", include_granted_scopes="true")
