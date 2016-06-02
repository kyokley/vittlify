BEGIN;
    CREATE UNIQUE INDEX auth_user_username_insensitive ON auth_user(lower(username));
COMMIT;
