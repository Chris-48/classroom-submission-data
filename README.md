# classroom submission data project

Allow the user to export classroom submission data to google sheets

    CREATE TABLE classroom_credentials(
        user_id TEXT,
        token TEXT,
        token_uri TEXT,
        client_id TEXT,
        refresh_token TEXT,
        client_secret TEXT,
        scopes TEXT
    );
    CREATE INDEX user_index ON classroom_credentials (user_id);
