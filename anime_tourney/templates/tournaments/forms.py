from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField


class NewUserTournamentForm(FlaskForm):
    starting_sizes = SelectField('Tournament Starting Size', coerce=int)
    submit = SubmitField('Begin')
