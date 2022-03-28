-- sqlite3
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS `songs` (
    `id` integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    `user_id` integer not null,
    `name` text NOT NULL,
    `artist` text default "Unknown",
    `creation` text NOT NULL, -- datetime
    `uploaded` text NOT NULL -- datetime add current time from python
);
CREATE TABLE IF NOT EXISTS `users` (
    `id` integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    `username` text default NULL,
    `password` varchar(255) NOT NULL
);
END TRANSACTION;