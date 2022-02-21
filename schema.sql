DROP TABLE IF EXISTS users;

CREATE TABLE users
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL
);

DROP TABLE IF EXISTS posts;

CREATE TABLE posts
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    background TEXT NOT NULL,
    submission_time TEXT NOT NULL,
    likes INTEGER NOT NULL
);

DROP TABLE IF EXISTS comments;

CREATE TABLE comments
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    author_name TEXT NOT NULL,
    comment TEXT NOT NULL,
    submission_time TEXT NOT NULL
);

-- create dummy data
INSERT INTO users (username, password_hash)
VALUES
    ('colm', 123),
    ('john', 456),
    ('mike', 789);

INSERT INTO posts (author_id, message, background, submission_time, likes)
VALUES
       (1, 'hello', 'blue', '2022-02-18 12:12:12', 69),
       (2, 'world', 'red', '2022-02-17 13:13:13', 420),
       (3, '!!!!!!!!!!!', 'pink', '2022-02-19-13:47:23', -5);