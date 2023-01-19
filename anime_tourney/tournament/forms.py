from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField


class NewUserTournamentForm(FlaskForm):
    starting_sizes = SelectField('Tournament Starting Size', coerce=int)
    submit = SubmitField('Begin')

class VerifyUserTournamentForm(FlaskForm):
    modal_title = StringField('You already have an exisitng tourney for this tournament')
    existing = SubmitField('My Tournaments')
    new = SubmitField('Create New')
