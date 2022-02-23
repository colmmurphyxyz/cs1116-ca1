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
    author_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    background TEXT NOT NULL,
    submission_time TEXT NOT NULL
);
DROP TABLE IF EXISTS likes;

CREATE TABLE likes
(
    post_id INTEGER NOT NULL,
    liker_id INTEGER NOT NULL
);""")
    write_dummy_user_rows(file)
    write_dummy_post_rows(file)
    file.close()


def write_dummy_post_rows(file):
    background_choices = ["red", "blue", "pink", "yellow", "green"]
    file.write("""INSERT INTO POSTS (author_id, message, background, submission_time, likes) VALUES\n""")
    likesFile = open("populate_likes_table.sql", "a")
    likesFile.write("""INSERT INTO likes (post_id, liker_id) VALUES\n""")
    for i in range(1, 1001):
        author_id = randint(1, num_users)
        background = choice(background_choices)

        # create a row in the likes table for every like the post has
        likes = randint(0, 300)
        for j in range(likes):
            likesFile.write(f"({i}, {randint(0, num_users)}),\n")

        # generate a string of gibberish for the post
        text = faker.paragraph(nb_sentences=randint(2, 4), variable_nb_sentences=True)
        # posted sometime in 2022
        start_date = datetime.strptime("2022-01-01 12:00:00", "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime("2022-12-31 12:00:00", "%Y-%m-%d %H:%M:%S")
        submission_time = faker.date_time_between(start_date, end_date).strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"   ({author_id}, '{text}', '{background}', '{submission_time}'),\n")
    file.write("    (1, 'Hello World', 'green', '2022-03-02 13:31:31', 123);")
    likesFile.write("(69, 429);")
    likesFile.close()

def write_dummy_user_rows(file):
    file.write("INSERT INTO users (username, password_hash) VALUES\n")
    for i in range(100):
        username = faker.user_name()
        password = generate_password_hash(faker.slug())
        file.write(f"    ('{username}', '{password}'),\n")
    file.write(f"    ('cooldude456', '{generate_password_hash('cftuygvbuh')}');\n")


if __name__ == "__main__":
    main()
