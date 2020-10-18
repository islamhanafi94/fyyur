from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

db = SQLAlchemy()


def db_init(app):
    db.init_app(app)
    Migrate(app, db)
    return db


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    website_link = db.Column(db.String(120), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(255), default='')
    genres = db.Column(db.ARRAY(db.String), nullable=False)

    def venue_data(self):
        upcoming_shows = self.get_upcoming_shows()
        past_shows = self.get_past_shows()
        return {
            "id": self.id,
            "name": self.name,
            "genres": self.genres,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "website": self.website_link,
            "facebook_link": self.facebook_link,
            "seeking_talent": self.seeking_talent,
            "seeking_description": self.seeking_description,
            "image_link": self.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }

    def get_past_shows(self):
        past_shows = []
        today_time = datetime.today()
        for show in self.shows:
            if show.start_time <= today_time:
                past_shows.append({
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": str(show.start_time)
                })
        return past_shows

    def get_upcoming_shows(self):
        upcoming_shows = []
        today_time = datetime.today()
        for show in self.shows:
            if show.start_time > today_time:
                upcoming_shows.append({
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": str(show.start_time)
                })
        return upcoming_shows

    def search_result(self):
        return {
            "id": self.id,
            "name": self.name,
            "num_upcoming_shows": len(self.get_upcoming_shows())
        }


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(120), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(255), default='')
    genres = db.Column(db.ARRAY(db.String), nullable=False)

    def artist_data(self):
        upcoming_shows = self.get_upcoming_shows()
        past_shows = self.get_past_shows()
        return {
            "id": self.id,
            "name": self.name,
            "genres": self.genres,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "website": self.website_link,
            "facebook_link": self.facebook_link,
            "seeking_venue": self.seeking_venue,
            "seeking_description": self.seeking_description,
            "image_link": self.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }

    def get_past_shows(self):
        past_shows = []
        today_time = datetime.today()
        for show in self.shows:
            if show.start_time <= today_time:
                past_shows.append({
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "venue_image_link": show.venue.image_link,
                    "start_time": str(show.start_time)
                })
        return past_shows

    def get_upcoming_shows(self):
        upcoming_shows = []
        today_time = datetime.today()
        for show in self.shows:
            if show.start_time > today_time:
                upcoming_shows.append({
                    "artist_id": show.artist_id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": str(show.start_time)
                })
        return upcoming_shows

    def search_result(self):
        return {
            "id": self.id,
            "name": self.name,
            "num_upcoming_shows": len(self.get_upcoming_shows())
        }


class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist = db.relationship('Artist',
                             backref=db.backref('shows', cascade="all, delete"), lazy=True)
    venue = db.relationship('Venue',
                            backref=db.backref('shows', cascade="all, delete"), lazy=True)

    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), nullable=False)
    venue_id = db.Column(
        db.Integer, db.ForeignKey('venue.id'), nullable=False)

    def show_data(self):
        return {
            "venue_id": self.venue_id,
            "venue_name": self.venue.name,
            "artist_id": self.artist_id,
            "artist_name": self.artist.name,
            "artist_image_link": self.artist.image_link,
            "start_time": str(self.start_time)
        }
