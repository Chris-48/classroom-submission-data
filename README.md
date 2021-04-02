# classroom submission data project

Allow the user to export classroom submission data to google sheets


### classroom credentials table


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


### google sheets credentials table


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