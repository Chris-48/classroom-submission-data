from sqlite3 import connect
from flask import session
import google.oauth2.credentials

# The database file
DATABASE = "credentials.db"


def get_credentials(servise: str) ->  google.oauth2.credentials.Credentials:
    """ 
    Get the credentials for the servise from the database \n
    return None if it hasn't found
    """

    # SQL query to get the credentials for the current user from servise credentials table
    query = f"""
        SELECT token, token_uri, client_id, refresh_token, client_secret, scopes
        FROM {servise}_credentials
        WHERE user_id=?;
    """

    # Get the credentials
    with connect(DATABASE) as db:
        credentials = db.execute(query, (session["user_id"],)).fetchone()

    # Return None if it doesn't exist it the database
    if not credentials: return None

    # Transfer the credentials to a dictionary
    credentials_dict = {
        "token": credentials[0],
        "token_uri": credentials[1],
        "client_id": credentials[2],
        "refresh_token": credentials[3],
        "client_secret": credentials[4],
        "scopes": None if credentials[5] is None else credentials[5].split(" ")
    }

    # Return a google Credentials object
    return google.oauth2.credentials.Credentials(**credentials_dict)


def store_credentials(servise: str, credentials) -> None:
    """ Store the user servise credentials on the database """

    # The data to be stoted in the database
    query_data = (
        credentials.token,
        credentials.token_uri,
        credentials.client_id,
        credentials.refresh_token, 
        credentials.client_secret, 
        " ".join(credentials.scopes),
        session["user_id"]
    )

    with connect(DATABASE) as db:

        # If the servise credentials for the current user exist in the database
        exist = db.execute(
            f"SELECT 1 FROM {servise}_credentials WHERE user_id=?",
            (session["user_id"],)
        ).fetchone()

        # If it exist the query should update it 
        if exist:
            query = f"""
                UPDATE {servise}_credentials
                SET token=?, token_uri=?, client_id=?, refresh_token=?, client_secret=?, scopes=?
                WHERE user_id=?;
            """
        # Else the query should add it to the database
        else:
            query = f"""
                INSERT INTO {servise}_credentials 
                (token, token_uri, client_id, refresh_token, client_secret, scopes, user_id)
                VALUES (?,?,?,?,?,?,?);
            """

        # Execute the query
        db.execute(query, query_data)
        db.commit()


def remove_credentials(service: str) -> None:
    """ Remove the servise credentials from the database """    
    
    # SQL query to remove the user servise credentials from the database
    query = f"DELETE FROM {service}_credentials WHERE user_id=?;"

    # Execute the query
    with connect(DATABASE) as db:    
        db.execute(query, (session["user_id"],))
        db.commit()
