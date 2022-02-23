from flask import Flask, render_template, request, redirect
from werkzeug.security import generate_password_hash
from database import get_db, close_db
from forms import HomePageForm, SignUpForm
from datetime import *

app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config["SECRET_KEY"] = "super-secret-key"

@app.route("/")
def root():
    # check if user already logged in
    # if not, redirect them to login/signup page
    # else, show them the homepage
    return redirect("http://127.0.0.1:5000/home", code=302)

@app.route("/home",  methods=["GET", "POST"])
def home():
    db = get_db()
    form = HomePageForm()
    sort_by = form.sort_by.data
    recent = form.recent.data

    query = "SELECT message, background, submission_time, likes FROM posts WHERE submission_time >= "
    if recent == "today":
        query += "datetime('now', '-24 hours')"
    elif recent == 'this week':
        query += "datetime('now', '-7 days')"
    elif recent == 'this month':
        query += "datetime('now', '-31 days')"
    else:   # elif recent == 'all time':
        query += "0"
    query += " AND submission_time <= datetime('now') "
    if sort_by == "most recent":
        query += "ORDER BY submission_time DESC"
    else:   # elif sort_by == "most popular"
        query += "ORDER BY likes DESC"     # i haven't implemented likes yet lol
    query += ";"

    posts = db.execute(query).fetchall()
    posts_formatted = []
    for post in posts:
        posts_formatted.append(
            {
                "message": post["message"],
                "background": post["background"],
                "submission_time": datetime.strptime(post["submission_time"], "%Y-%m-%d %H:%M:%S").strftime("%d %b"),
                "likes": post["likes"]
            }
        )
    return render_template("home.html", form=form, posts=posts_formatted)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    username = ""
    password = ""
    if form.validate_on_submit():
        username = form.username.data
        password_hash = generate_password_hash(form.password.data)
        db = get_db()
        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        db.commit()
    return render_template("signup.html", form=form)
