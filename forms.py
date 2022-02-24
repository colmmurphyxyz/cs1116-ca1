from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import EqualTo, InputRequired, Length


class HomePageForm(FlaskForm):
    sort_by = SelectField(label="Show me the ", choices=["most recent", "most popular"],
                          default="most recent")
    recent = SelectField(label="posts from", choices=["today", "this week", "this month", "all time"],
                         default="this week")
    submit = SubmitField("Submit")


class SignUpForm(FlaskForm):
    username = StringField("Username:",
                           validators=[InputRequired(), Length(4, 20)])
    password = PasswordField("Password:",
                             validators=[InputRequired(), Length(min=6)])
    password2 = PasswordField("Re-enter your password",
                              validators=[EqualTo("password")])
    submit = SubmitField()


class LoginForm(FlaskForm):
    username = StringField("Username:",
                           validators=[InputRequired(), Length(4, 20)])
    password = PasswordField("Password",
                             validators=[InputRequired(), Length(min=6)])
    submit = SubmitField()
