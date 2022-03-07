from flask import Flask, render_template, request, redirect, url_for, g, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from database import get_db, close_db
from forms import CommentForm, HomePageForm, RegistrationForm, LoginForm, CreatePostForm, color_scheme
from datetime import *

app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config["SECRET_KEY"] = "super-secret-key"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def current_datetime_sql_format():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.before_request
def load_logged_in_user():
    g.user = session.get("username", None)

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.url))
        return view(**kwargs)

    return wrapped_view

@app.route("/")
def root():
    return render_template("base.html")

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
            FROM posts
            WHERE submission_time <= datetime('now') and submission_time >= {recent_posts_limit}
            ORDER BY submission_time DESC;"""
    else:  # if sort_by == "most popular
        query = f"""SELECT id, message, background, submission_time, COUNT(*)
        FROM posts JOIN likes
            ON posts.id == likes.post_id
        WHERE submission_time BETWEEN {recent_posts_limit} AND datetime('now')
        GROUP BY post_id
        ORDER BY COUNT(*) DESC;"""
        # ^ this query will not select posts with 0 likes. It's a design choice, not an error7 ;)

    posts = db.execute(query).fetchall()
    posts_formatted = []
    for post in posts:
        likes = db.execute("SELECT COUNT(*) AS 'likes' FROM likes WHERE post_id = ?;", (post["id"],)).fetchone()[
            "likes"]
        is_liked_by_user = db.execute("""SELECT * FROM
                posts JOIN likes
                    ON posts.id = ?
                        AND posts.id = likes.post_id
                WHERE likes.liker = ?;""", (post["id"], session.get("username", ""))).fetchone() is not None
        num_comments = db.execute("""SELECT COUNT(*)
                FROM comments
                WHERE post_id = ?;""", (post["id"],)).fetchone()["COUNT(*)"]
        posts_formatted.append(
            {
                "id": post["id"],
                "message": post["message"],
                "background": post["background"],
                "submission_time": datetime.strptime(post["submission_time"], "%Y-%m-%d %H:%M:%S").strftime("%d %b"),
                "likes": likes,
                "is_liked": is_liked_by_user,
                "num_comments": num_comments
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
        possible_matching_user = db.execute("SELECT * FROM users WHERE username = ?;",
                                            (username,)).fetchone()
        if possible_matching_user is None:
            form.username.errors.append("There is no user called %s" % username)
            return render_template("login.html", form=form, message="")
        else:
            password_in_db = db.execute("SELECT password_hash FROM users WHERE username = ?;",
                                        (username,)).fetchone()["password_hash"]
        password_correct = check_password_hash(password_in_db, password)
        if not password_correct:
            form.password.errors.append("Incorrect password :(")
        else:
            session.clear()
            session["username"] = username
            next_page = request.args.get("next")
            if not next_page:
                next_page = url_for("home")
            return redirect(next_page)
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        db = get_db()
        possible_clashing_user = db.execute("SELECT * FROM users WHERE username = ?;", (username,)).fetchone()
        if possible_clashing_user is not None:
            form.username.errors.append(f"{username} is already taken")
        else:
            db.execute("""INSERT INTO users (username, password_hash) VALUES
                (?, ?);""", (username, generate_password_hash(password)))
            db.commit()
            return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/create_post", methods=["GET", "POST"])
@login_required
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        message = form.message.data
        color = form.color.data
        db = get_db()
        submission_time = current_datetime_sql_format()
        db.execute("""INSERT INTO posts (author, message, background, submission_time) VALUES
        (?, ?, ?, ?);""", (session["username"], message, color_scheme[color], submission_time))
        db.commit()
        return redirect(url_for("home"))
    return render_template("create_post.html", form=form)

@app.route("/like_post/<int:post_id>")
@login_required
def like_post(post_id):
    db = get_db()
    post_already_liked = db.execute("""SELECT * FROM likes WHERE post_id = ? AND liker = ?;""",
                                    (post_id, session["username"])).fetchone() is not None
    if not post_already_liked:
        db.execute("""INSERT INTO likes (post_id, liker) VALUES
                (?, ?);""", (post_id, session["username"]))
        db.commit()
    return redirect(url_for("home"))

@app.route("/unlike_post/<int:post_id>")
@login_required
def unlike_post(post_id):
    db = get_db()
    db.execute("""DELETE FROM likes
            WHERE post_id = ? AND liker = ?;""", (post_id, session["username"]))
    db.commit()
    return redirect(url_for("home"))

@app.route("/view_comments/<int:post_id>", methods=["GET", "POST"])
@login_required
def view_comments(post_id):
    form = CommentForm()
    db = get_db()
    post = db.execute("""SELECT id, message, background, submission_time FROM posts WHERE id = ?;""",
                      (post_id,)).fetchone()

    if form.validate_on_submit():
        comment = form.comment.data
        db.execute("""INSERT INTO comments (post_id, author, content, submission_time) VALUES
                    (?, ?, ?, ?);""", (post["id"], session["username"], comment, current_datetime_sql_format()))
        db.commit()

    comments = db.execute("""SELECT author, content
        FROM comments
        WHERE post_id = ?;""", (post_id,)).fetchall()
    likes = db.execute("SELECT COUNT(*) AS 'likes' FROM likes WHERE post_id = ?;", (post["id"],)).fetchone()["likes"]
    return render_template("view_comments.html", post=post, comments=comments, likes=likes, form=form)
