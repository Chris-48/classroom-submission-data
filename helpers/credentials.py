import google_auth_oauthlib
from flask.helpers import url_for


def create_credentials(service: str, client_secret, scopes, state, url):
    """ Create the servise credentials """

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
    """ Create the url where the user should grant authorization """

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_secret,
        scopes=scopes
    )

    flow.redirect_uri = url_for(f"{service}_oauth2callback", _external=True)

    return flow.authorization_url(access_type="offline", include_granted_scopes="true")
