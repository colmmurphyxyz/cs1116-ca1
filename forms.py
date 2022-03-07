from flask_wtf import FlaskForm
from wtforms import PasswordField, RadioField, SelectField, StringField, SubmitField
from wtforms.validators import EqualTo, InputRequired, Length

color_scheme = {"congo-pink": "#ff7070",
                "blue-purple":  "#adadff",
                "tea-green": "#adffad",
                "piggy-pink": "#ffd6dd",
                "laser-lemon": "#ffff5c"}

class HomePageForm(FlaskForm):
    sort_by = SelectField(label="Show me the ", choices=["most recent", "most popular"],
                          default="most recent")
    recent = SelectField(label="posts from", choices=["today", "this week", "this month", "all time"],
                         default="this week")
    submit = SubmitField("Submit")


class RegistrationForm(FlaskForm):
    username = StringField("Username:",
                           validators=[InputRequired(), Length(4, 20)])
    password = PasswordField("Password",
                             validators=[InputRequired(), Length(min=6)])
    password2 = PasswordField("Re-enter password:",
                              validators=[InputRequired(), EqualTo("password")])
    submit = SubmitField()

class LoginForm(FlaskForm):
    username = StringField("Username:",
                           validators=[InputRequired(), Length(4, 20)])
    password = PasswordField("Password",
                             validators=[InputRequired(), Length(min=6)])
    submit = SubmitField()

class CreatePostForm(FlaskForm):
    message = StringField("Post:",
                          validators=[InputRequired(), Length(8, 240)])
    color = RadioField("Background colour",
                       validators=[InputRequired()],
                       choices=color_scheme.keys())
    submit = SubmitField()

class CommentForm(FlaskForm):
    comment = StringField("Comment:",
                          validators=[InputRequired(), Length(max=150)])
    submit = SubmitField()
