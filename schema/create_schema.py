from random import choice, randint
from faker import *
from werkzeug.security import generate_password_hash
from datetime import datetime

num_users = 100
max_likes = 1000

faker = Faker()

"""
PYCharm will freeze/crash when attempting to run schema.sql or populate_likes_table.sql.
Use the 'deploy_schema' script instead.
"""

def main():
    file = open("schema.sql", "a")
    file.write("""DROP TABLE IF EXISTS users;
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
    author TEXT NOT NULL,
    message TEXT NOT NULL,
    background TEXT NOT NULL,
    submission_time TEXT NOT NULL
);

DROP TABLE IF EXISTS likes;

CREATE TABLE likes
(
    post_id INTEGER NOT NULL,
    liker TEXT NOT NULL
);

DROP TABLE IF EXISTS comments;

CREATE TABLE comments
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    author TEXT NOT NULL,
    content TEXT NOT NULL,
    submission_time TEXT NOT NULL
);

""")

    write_dummy_user_rows(file)
    write_dummy_post_rows(file)
    write_dummy_comment_rows(file)
    file.close()

def random_datetime_this_year():
    start_date = datetime.strptime("2022-01-01 12:00:00", "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime("2022-12-31 12:00:00", "%Y-%m-%d %H:%M:%S")
    return faker.date_time_between(start_date, end_date).strftime("%Y-%m-%d %H:%M:%S")


def write_dummy_post_rows(file):
    color_scheme = ["#ff7070", "#adadff", "#adffad", "#ffd6dd", "#ffff5c"]
    file.write("""INSERT INTO POSTS (author, message, background, submission_time) VALUES\n""")
    likesFile = open("populate_likes_table.sql", "a")
    likesFile.write("""INSERT INTO likes (post_id, liker) VALUES\n""")
    for i in range(1, 1001):
        author = faker.user_name()
        background = choice(color_scheme)

        # create a row in the likes table for every like the post has
        likes = randint(0, 300)
        for j in range(likes):
            likesFile.write(f"({i}, '{faker.user_name()}'),\n")

        # generate a string of gibberish for the post
        text = faker.paragraph(nb_sentences=randint(2, 4), variable_nb_sentences=True)
        # posted sometime in 2022
        submission_time = random_datetime_this_year()
        file.write(f"   ('{author}', '{text}', '{background}', '{submission_time}'),\n")
    file.write("    ('colmmurphy', 'Hello World', 'green', '2022-03-02 13:31:31');")
    likesFile.write("(1001, 'colmmurphy');")
    likesFile.close()

def write_dummy_user_rows(file):
    file.write("INSERT INTO users (username, password_hash) VALUES\n")
    for i in range(100):
        username = faker.user_name()
        password = generate_password_hash(faker.slug())
        file.write(f"    ('{username}', '{password}'),\n")
    file.write(f"    ('cooldude456', '{generate_password_hash('cftuygvbuh')}');\n")

def write_dummy_comment_rows(file):
    file.write("INSERT INTO comments (post_id, author, content, submission_time) VALUES\n")
    for i in range(1001):
        for j in range(randint(0, 5)):
            author = faker.user_name()
            content = faker.paragraph(nb_sentences=randint(1, 4), variable_nb_sentences=True)
            submission_time = random_datetime_this_year()
            file.write(f"    ({i}, '{author}', '{content}', '{submission_time}'),\n")
    file.write("    (123, 'colmmurphy', 'testing', '2022-06-06 12:12:12');\n")


if __name__ == "__main__":
    main()
