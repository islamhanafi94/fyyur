#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, abort, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form, CSRFProtect
from forms import *
from flask_migrate import Migrate


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

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


class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist = db.relationship('Artist', backref='shows',
                             cascade="all, delete", lazy=True)
    venue = db.relationship('Venue', backref='shows',
                            cascade="all, delete", lazy=True)

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


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # print()
    distict_areas = Venue.query.options(load_only('city', 'state')).distinct(
        Venue.city, Venue.state).all()
    all_venues = Venue.query.all()

    data = []
    for area in distict_areas:
        venues = []
        for venue in all_venues:
            if venue.state == area.state and venue.city == area.city:
                venues.append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": 5
                })
        data.append({
            "city": area.city,
            "state": area.state,
            "venues": venues
        })

    return render_template('pages/venues.html', areas=data)


@ app.route('/venues/search', methods=['POST'])
def search_venues():
    q = request.form.get('search_term')
    result = Venue.query.filter(Venue.name.ilike(f'%{q}%')).all()
    response = {
        "count": len(result),
        "data": [venue.search_result() for venue in result]
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if not venue:
        abort(404)
    return render_template('pages/show_venue.html', venue=venue.venue_data())


#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm()
    if not form.validate_on_submit():
        flash('Please Provide valid Venue Information')
        return redirect(url_for('create_venue_form'))

    try:
        data = {
            'name': form.data.get('name'),
            'city': form.data.get('city'),
            'state': form.data.get('state'),
            'address': form.data.get('address'),
            'phone': form.data.get('phone'),
            'genres': form.data.get('genres'),
            'website_link': form.data.get('website_link'),
            'image_link': form.data.get('image_link'),
            'facebook_link': form.data.get('facebook_link'),
            'seeking_talent': form.data.get('seeking_talent'),
            'seeking_description': form.data.get('seeking_description')
        }
        new_venue = Venue(**data)
        db.session.add(new_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] +
              ' was successfully listed!')
    except Exception as e:
        print(e)
        db.session.rollback()
        flash('Error !! .. Venue ' +
              request.form['name'] + 'is not added !!')
        return redirect(url_for('create_venue_form'))
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE', 'POST'])
def delete_venue(venue_id):
    if request.form.get('delete') == 'Delete':
        # check the user_id
        venue = Venue.query.get(venue_id)
        if not venue:
            return redirect(url_for('index'))

        try:
            db.session.delete(venue)
            db.session.commit()
            flash(f'Venue : {venue.name} is successfuly deleted !!')
        except Exception as ex:
            db.session.rollback()
            flash('operation failed !!')
        finally:
            db.session.close()

    return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    q = request.form.get('search_term')
    result = Artist.query.filter(Artist.name.ilike(f'%{q}%')).all()
    response = {
        "count": len(result),
        "data": [artist.search_result() for artist in result]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if not artist:
        abort(404)
    return render_template('pages/show_artist.html', artist=artist.artist_data())


#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if not artist:
        abort(404)
    form = ArtistForm(data=artist.artist_data())
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm()
    if not form.validate_on_submit():
        flash('Please Provide valid Artist Information')
        return redirect(url_for('edit_artist', artist_id=artist_id))

    artist = Artist.query.get(artist_id)

    try:
        artist.name = form.data.get('name')
        artist.city = form.data.get('city')
        artist.state = form.data.get('state')
        artist.phone = form.data.get('phone')
        artist.genres = form.data.get('genres')
        artist.website_link = form.data.get('website_link')
        artist.image_link = form.data.get('image_link')
        artist.facebook_link = form.data.get('facebook_link')
        artist.seeking_venue = form.data.get('seeking_venue')
        artist.seeking_description = form.data.get('seeking_description')
        db.session.commit()
        flash('Artest ' + request.form['name'] +
              ' was successfully listed!')
    except Exception as e:
        print(e)
        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be Updated.')
        return redirect(url_for('edit_artist', artist_id=artist_id))
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if not venue:
        abort(404)

    form = VenueForm(data=venue.venue_data())

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm()
    if not form.validate_on_submit():
        flash('Please Provide valid Artist Information')
        return redirect(url_for('edit_venue', venue_id=venue_id))

    venue = Venue.query.get(venue_id)
    try:
        venue.name = form.data.get('name')
        venue.city = form.data.get('city')
        venue.state = form.data.get('state')
        venue.address = form.data.get('address')
        venue.phone = form.data.get('phone')
        venue.genres = form.data.get('genres')
        venue.website_link = form.data.get('website_link')
        venue.image_link = form.data.get('image_link')
        venue.facebook_link = form.data.get('facebook_link')
        venue.seeking_talent = form.data.get('seeking_talent')
        venue.seeking_description = form.data.get('seeking_description')
        db.session.commit()
        flash('Venue ' + request.form['name'] +
              ' was successfully listed!')
    except Exception as e:
        print(e)
        db.session.rollback()
        flash('Error !! .. Venue ' +
              request.form['name'] + 'is not added !!')
        return redirect(url_for('edit_venue_submission', venue_id=venue_id))
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm()
    if not form.validate_on_submit():
        flash('Please Provide valid Artist Information')
        return redirect(url_for('create_artist_form'))
    try:
        data = {
            'name': form.data.get('name'),
            'city': form.data.get('city'),
            'state': form.data.get('state'),
            'phone': form.data.get('phone'),
            'genres': form.data.get('genres'),
            'website_link': form.data.get('website_link'),
            'image_link': form.data.get('image_link'),
            'facebook_link': form.data.get('facebook_link'),
            'seeking_venue': form.data.get('seeking_venue'),
            'seeking_description': form.data.get('seeking_description')
        }
        new_artist = Artist(**data)
        db.session.add(new_artist)
        db.session.commit()
        flash('Artest ' + request.form['name'] +
              ' was successfully listed!')
    except Exception as e:
        print(e)
        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
        return redirect(url_for('create_artist_form'))
    finally:
        db.session.close()
    return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    shows = Show.query.all()
    data = [show.show_data() for show in shows]
    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm()
    if not form.validate_on_submit():
        flash('Please provide a valid show input')
        return redirect(url_for('create_shows'))

    try:
        data = {
            'start_time': form.data.get('start_time'),
            'venue_id': form.data.get('venue_id'),
            'artist_id': form.data.get('artist_id')
        }
        new_show = Show(**data)
        db.session.add(new_show)
        db.session.commit()
        flash('Show was successfully listed!')
    except Exception as e:
        print(e)
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
        return redirect(url_for('create_shows'))
    finally:
        db.session.close()

    return redirect(url_for('index'))


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
