-- sqlite3
BEGIN TRANSACTION;

-- Find a cleaner way to do this when porting this to postgres in the future
CREATE TABLE IF NOT EXISTS `ch_songs` (
    `song_id` integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    `user_id` integer not null,
    `song_name` text NOT NULL,
    `artist` text default "Unknown",
    `song_creation` text NOT NULL, -- datetime
    `uploaded` text NOT NULL -- datetime add current time from python
);

CREATE TABLE IF NOT EXISTS `osu_songs` (
    `song_id` integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    `user_id` integer not null,
    `song_name` text NOT NULL,
    `artist` text default "Unknown",
    `song_creation` text NOT NULL, -- datetime
    `uploaded` text NOT NULL -- datetime add current time from python
);

CREATE TABLE IF NOT EXISTS `users` (
    `id` integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    `username` text default NULL,
    `password` varchar(255) NOT NULL
);
END TRANSACTION;