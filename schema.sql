-- postgres 13 ;
-- TODO: rename to schema.sql;

CREATE SCHEMA IF NOT EXISTS rgsdb; -- not needed

-- OH GOD WHY

CREATE TABLE IF NOT EXISTS rgsdb.chsong (
    id BIGINT PRIMARY KEY,
    user_id INT NOT NULL,
    name TEXT NOT NULL,
    artist TEXT,
    uploaded DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS rgsdb.osusong (
    id BIGINT PRIMARY KEY,
    user_id INT NOT NULL,
    name TEXT NOT NULL,
    artist TEXT,
    uploaded DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS rgsdb.osuskin (
    id BIGINT PRIMARY KEY,
    user_id INT NOT NULL,
    name TEXT NOT NULL,
    uploaded DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS rgsdb.osureplay (
    id BIGINT PRIMARY KEY,
    user_id INT NOT NULL,
    player TEXT NOT NULL,
    name TEXT NOT NULL,
    uploaded DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS rgsdb.users (
    id SERIAL NOT NULL PRIMARY KEY,
    username TEXT NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);