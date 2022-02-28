from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, close_db
from forms import HomePageForm, SignUpForm, LoginForm, CreatePostForm, color_scheme
from datetime import *

app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config["SECRET_KEY"] = "super-secret-key"


@app.route("/")
def root():
    # check if user already logged in
    # if not, redirect them to login/signup page
    # else, show them the homepage
    return redirect(url_for("home"), code=302)


@app.route("/home", methods=["GET", "POST"])
def home():
    db = get_db()
    form = HomePageForm()
    sort_by = form.sort_by.data
    recent = form.recent.data

    if recent == "today":
        recent_posts_limit = "datetime('now', '-24 hours')"
    elif recent == "this week":
        recent_posts_limit = "datetime('now', '-7 days')"
    elif recent == "this month":
        recent_posts_limit = "datetime('now', '-31 days')"
    else:
        recent_posts_limit = "0"

    if sort_by == "most recent":
        query = f"""SELECT id, message, background, submission_time
        FROM posts JOIN likes
            ON posts.id == likes.post_id
        WHERE submission_time BETWEEN {recent_posts_limit} AND datetime('now')
        GROUP BY posts.id, submission_time
        ORDER BY submission_time DESC;"""
    else:   # if sort_by == "most popular
        query = f"""SELECT id, message, background, submission_time, COUNT(*)
        FROM posts JOIN likes
            ON posts.id == likes.post_id
        WHERE submission_time BETWEEN {recent_posts_limit} AND datetime('now')
        GROUP BY post_id
        ORDER BY COUNT(*) DESC;"""

    # query = """SELECT id, message, background, submission_time, COUNT(*) AS 'likes'
    #         FROM posts JOIN likes
    #             ON posts.id = likes.post_id
    #         WHERE submission_time >= """
    # if recent == "today":
    #     query += "datetime('now', '-24 hours')"
    # elif recent == 'this week':
    #     query += "datetime('now', '-7 days')"
    # elif recent == 'this month':
    #     query += "datetime('now', '-31 days')"
    # else:  # elif recent == 'all time':
    #     query += "0"
    # query += " AND submission_time <= datetime('now') "
    # query += "GROUP BY posts.id, posts.submission_time"
    # if sort_by == "most recent":
    #     query += "ORDER BY submission_time DESC"
    # else:  # elif sort_by == "most popular"
    #     query += "ORDER BY COUNT(*) DESC"
    # query += ";"

    print(f"{query}")
    posts = db.execute(query).fetchall()
    print(posts)
    posts_formatted = []
    for post in posts:
        likes = db.execute("SELECT COUNT(*) AS 'likes' FROM likes WHERE post_id = ?;", (post["id"],)).fetchone()[
            "likes"]
        posts_formatted.append(
            {
                "message": post["message"],
                "background": post["background"],
                "submission_time": datetime.strptime(post["submission_time"], "%Y-%m-%d %H:%M:%S").strftime("%d %b"),
                "likes": likes
            }
        )
    return render_template("home.html", form=form, posts=posts_formatted)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        db = get_db()

        username_exists_in_db = db.execute("SELECT * FROM users WHERE username = ?;",
                                           (username,)).fetchone().keys() != 0
        if not username_exists_in_db:
            form.username.errors.append("There is no user called %s" % username)
            return render_template("login.html", form=form, message="")
        password_in_db = db.execute("SELECT password_hash FROM users WHERE username = ?;",
                                    (username,)).fetchone()["password_hash"]
        password_correct = check_password_hash(password_in_db, password)
        if not password_correct:
            form.password.errors.append("Incorrect password :(")
            return render_template("login.html", form=form, message=f"You are now logged in as {username}")

        return render_template("login.html", form=form, message=f"You are now logged in as {username}")
    return render_template("login.html", form=form)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        username = form.username.data
        password_hash = generate_password_hash(form.password.data)
        db = get_db()
        # validations
        users_with_same_name = db.execute("""
        SELECT COUNT(*) AS 'users_with_same_name'
        FROM users 
        WHERE username = ?;""",
                                          (username,)).fetchone()["users_with_same_name"]
        if users_with_same_name > 0:
            form.username.errors.append(username + " is already taken")
            return render_template("signup.html", form=form)
        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        db.commit()
        return redirect(url_for("home"), code=302)
    return render_template("signup.html", form=form)

@app.route("/create_post", methods=["GEt", "POST"])
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        message = form.message.data
        color = form.color.data
        db = get_db()
        submission_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute("""INSERT INTO posts (author_id, message, background, submission_time) VALUES
        (420, ?, ?, ?);""", (message, color_scheme[color], submission_time))
        db.commit()
    return render_template("create_post.html", form=form)
