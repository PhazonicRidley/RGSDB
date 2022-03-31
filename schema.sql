-- postgres 13 ;
-- TODO: rename to schema.sql;

CREATE SCHEMA IF NOT EXISTS rgsdb; -- not needed

CREATE TABLE IF NOT EXISTS rgsdb.data (
    id BIGINT PRIMARY KEY,
    user_id INT NOT NULL,
    name TEXT NOT NULL,
    artist TEXT,
    type TEXT NOT NULL,
    uploaded DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS rgsdb.users (
    id SERIAL NOT NULL PRIMARY KEY,
    username TEXT NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);