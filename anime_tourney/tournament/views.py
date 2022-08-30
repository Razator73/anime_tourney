# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template, redirect, url_for, abort, current_app
from flask_login import login_required, current_user

from anime_tourney.extensions import db
from anime_tourney.templates.tournaments.forms import NewUserTournamentForm
from anime_tourney.tournament.models import Tournament, UserTournament, Round, Match, Contestant

blueprint = Blueprint("tournament", __name__, url_prefix="/tournaments", static_folder="../static")


@blueprint.route("/")
@login_required
def index():
    """List tournaments."""
    return render_template("tournaments/tournaments.html", tournaments=Tournament.query.all())


@blueprint.route('/create/<tid>', methods=['GET', 'POST'])
@login_required
def create(tid):
    # redirect(url_for('tournament.current_match', tid=tid))
    tourney_contestants = Contestant.query.filter_by(tournament_id=tid).all()
    create_form = NewUserTournamentForm()
    size = 2
    starting_sizes = []
    current_app.logger.info(len(tourney_contestants))
    while size <= len(tourney_contestants):
        current_app.logger.info((size, f'Round of {size}'))
        starting_sizes.append((size, f'Round of {size}'))
        size *= 2
    create_form.starting_sizes.choices = starting_sizes
    if create_form.validate_on_submit():
        current_app.logger.debug(f'data - {create_form.starting_sizes.data}')
        user_tournament = UserTournament.create(user_id=current_user.id, tournament_id=tid)
        first_round = Round.create(user_tournament_id=user_tournament.id, size=create_form.starting_sizes.data)
        first_round.set_contestants()
        first_round.create_matches()
        return redirect(url_for('tournament.current_match', tid=user_tournament.id))
    return render_template('tournaments/new_tournament.html', tournaments=Tournament.query.all(), form=create_form)


@blueprint.route('/user')
@login_required
def user_tournaments():
    """List tournaments open for the user"""
    return render_template("tournaments/user_tournaments.html",
                           tournaments=current_user.user_tournaments)


@blueprint.route('/user/<tid>/current_match', methods=["GET", "POST"])
@login_required
def current_match(tid):
    user_tourney = UserTournament.get_by_id(tid)
    if user_tourney.is_complete:
        return redirect(url_for('tournament.victor_page', tid=tid))
    elif not user_tourney:
        abort(404)

    current_round = Round.query.filter_by(user_tournament_id=tid).filter_by(is_complete=False)\
        .order_by(Round.size.desc()).first()
    cur_match = Match.query.filter_by(round_id=current_round.id).filter_by(victor_id=None).first()
    complete_matches = len([match for match in current_round.matches if match.victor_id]) + 1
    return render_template('tournaments/current_match.html', round=current_round, match=cur_match,
                           complete_matches=complete_matches)


@blueprint.route('/<match_id>/<victor_id>')
@login_required
def pick_victor(match_id, victor_id):
    match = Match.get_by_id(match_id)
    match.victor_id = victor_id
    match.next_round.contestants.append(Contestant.get_by_id(victor_id))
    if not [m for m in match.round.matches if not m.victor_id]:
        if match.next_round.size == 1:
            match.next_round.is_complete = True
            match.round.user_tournament.is_complete = True
        else:
            match.next_round.create_matches()
        match.round.is_complete = True
    match.save()
    db.session.commit()
    return redirect(url_for('tournament.current_match', tid=match.round.user_tournament_id))


@blueprint.route('/user/<tid>/victor')
@login_required
def victor_page(tid):
    final_round = Round.query.filter_by(user_tournament_id=tid).filter_by(size=1).first()
    winner = final_round.contestants[0]
    return render_template('tournaments/victor.html', winner=winner)
