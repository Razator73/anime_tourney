"""Tournament models."""
from random import randint, sample

from anime_tourney.database import Column, PkModel, db, reference_col, relationship


class Tournament(PkModel):
    __tablename__ = "tournaments"

    name = Column(db.String(80), unique=True, nullable=False)


class UserTournament(PkModel):
    __tablename__ = 'user_tournaments'

    tournament_id = reference_col('tournaments')
    user_id = reference_col('users')
    is_complete = db.Column(db.BOOLEAN, default=False, nullable=False)
    tournament = relationship('Tournament', backref='user_tournaments')
    user = relationship('User', backref='user_tournaments')
    rounds = relationship('Round', backref='user_tournament')


round_contestants = db.Table(
    'round_contestants',
    db.Column('round_id', db.Integer, db.ForeignKey('rounds.id'), primary_key=True),
    db.Column('contestant_id', db.Integer, db.ForeignKey('contestants.id'), primary_key=True)
)


class Contestant(PkModel):
    __tablename__ = 'contestants'

    name = Column(db.String(127), nullable=False)
    video_id = Column(db.String(16), unique=True, nullable=False)
    bad_video = Column(db.BOOLEAN, nullable=False, default=False)
    tournament_id = reference_col('tournaments')
    tournament = relationship('Tournament', backref='contestants')


class Round(PkModel):
    __tablename__ = 'rounds'

    user_tournament_id = reference_col('user_tournaments')
    size = db.Column(db.Integer, nullable=False)
    is_complete = db.Column(db.BOOLEAN, default=False, nullable=False)
    contestants = relationship('Contestant', secondary=round_contestants, lazy='dynamic',
                               backref=db.backref('contestants', lazy='dynamic'))

    def set_contestants(self):
        contestants = list(Contestant.query.filter_by(tournament_id=self.user_tournament.tournament.id,
                                                      bad_video=False).all())
        if len(contestants) < self.size:
            self.contestants = sample(contestants, len(contestants))
        else:
            self.contestants = sample(contestants, self.size)

    def create_matches(self):
        if self.size > 1:
            contestants = list(self.contestants)
            next_round = Round.create(user_tournament_id=self.user_tournament_id, size=self.size // 2)
            matches = []
            if self.size > len(contestants):
                while len(contestants) > next_round.size:
                    if randint(0, 1):
                        matches.append((contestants.pop(randint(0, len(contestants) - 1)).id, None))
                    else:
                        matches.append((None, contestants.pop(randint(0, len(contestants) - 1)).id))
            while contestants:
                matches.append((contestants.pop(randint(0, len(contestants) - 1)).id,
                                contestants.pop(randint(0, len(contestants) - 1)).id))
            while matches:
                match = matches.pop(randint(0, len(matches) - 1))
                Match.create(
                    round_id=self.id, first_contestant_id=match[0],
                    second_contestant_id=match[1],
                    next_round_id=next_round.id
                )


class Match(PkModel):
    __tablename__ = 'matches'

    round_id = reference_col('rounds')
    first_contestant_id = reference_col('contestants', nullable=True)
    second_contestant_id = reference_col('contestants', nullable=True)
    victor_id = reference_col('contestants', nullable=True)
    next_round_id = reference_col('rounds')
    round = relationship('Round', foreign_keys=[round_id], backref='matches')
    next_round = relationship('Round', foreign_keys=[next_round_id])
    first_contestant = relationship('Contestant', foreign_keys=[first_contestant_id])
    second_contestant = relationship('Contestant', foreign_keys=[second_contestant_id])
    victor = relationship('Contestant', foreign_keys=[victor_id])
