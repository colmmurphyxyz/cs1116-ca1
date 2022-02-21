from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField

class HomePageForm(FlaskForm):
    sort_by = SelectField(label="Show me the ", choices=["most recent", "most popular"],
                          default="most recent")
    recent = SelectField(label="posts from", choices=["today", "this week", "this month", "all time"],
                         default="this week")
    submit = SubmitField("Submit")
