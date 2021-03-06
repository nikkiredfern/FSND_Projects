#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime

# imported flask-migrate, datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database - COMPLETED, added migrate

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.String)
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.String)
    seeking_talent_description = db.Column(db.String())
    venue_shows = db.relationship('Show', backref='Venues', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # COMPLETED


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.String)
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.String())
    seeking_description = db.Column(db.String(1000))
    artist_shows = db.relationship('Show', backref='Artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate - COMPLETED

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. - COMPLETED


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=True)

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

@app.route('/venues', methods=['GET'])
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    locations = set()
    areas = Venue.query.all()
    for area in areas:
        locations.add((area.city, area.state))
    for location in locations:
        data.append({
            "city": location[0],
            "state": location[1],
            "venues": []
        })

    for area in areas:
        num_upcoming_shows = 0

        shows = Show.query.filter_by(venue_id=area.id).all()
        now = datetime.now()
        for show in shows:
            if show.start_time > now:
                num_upcoming_shows += 1

        for location in data:
            if area.state == location['state'] and area.city == location['city']:
                location['venues'].append({
                    "id": area.id,
                    "name": area.name,
                    "num_upcoming_shows": num_upcoming_shows
                })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
    response = {
        "count": len(venues),
        "data": venues
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>', methods=['GET'])
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    genres = venue.genres.split(",")

    data = {
        'id': venue.id,
        'name': venue.name,
        'address': venue.address,
        'genres': [item.replace('{', '').replace('}', '') for item in genres],
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website': venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'image_link': venue.image_link,
    }
    past_shows = db.session.query(Show.artist_id, Show.start_time).filter(
        Show.venue_id == venue.id, Show.start_time < datetime.now()).all()
    upcoming_shows = db.session.query(Venue).join(
        Show, Show.venue_id == venue.id).filter(Show.start_time > datetime.utcnow())
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    if request.method == 'POST':
        error = False
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        phone = request.form['phone']
        image_link = request.form['image_link']
        genres = request.form.getlist('genres')
        facebook_link = request.form['facebook_link']
        if 'seeking_talent' not in request.form:
            seeking_talent = False
        else:
            seeking_talent = request.form['seeking_talent']
        seeking_talent_description = request.form['seeking_talent_description']
        # TODO: modify data to be the data object returned from db insertion
        venue = Venue(name=name,
                      city=city,
                      state=state,
                      address=address,
                      phone=phone,
                      image_link=image_link,
                      genres=genres,
                      facebook_link=facebook_link,
                      seeking_talent=seeking_talent,
                      seeking_talent_description=seeking_talent_description)
        try:
            print(venue)
            db.session.add(venue)
            db.session.commit()
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        except:
            db.session.rollback()
            error = True
            # on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
            print(sys.exe_info())
        finally:
            db.session.close()

        return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>', methods=['POST'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        venue = Venue.query.filter_by(id=venue_id).first_or_404()
        db.session.delete(venue)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        flash('An error occured and venue, ' + venue.name + ', could not be deleted.')
        abort(500)
    else:
        flash('The venue, ' + venue.name + ', was deleted.')
        return render_template('pages/home.html')
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = []
    artists = Artist.query.all()
    for artist in artists:
        data.append(artist)

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
    response = {
        "count": len(artists),
        "data": artists
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    artist = Artist.query.get(artist_id)
    genres = artist.genres.split(',')
    now = datetime.utcnow()
    #shows = Show.query.fliter_by(artist_id=artist_id).all()
    find_upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id, Show.start_time > now).all()
    find_past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id, Show.start_time < now).all()
    upcoming_shows = []
    past_shows = []

    for show in find_upcoming_shows:
        upcoming_shows.append([{
            'venue_id': show.id,
            'venue_name': show.name,
            'image_link': show.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        }])

    for show in find_past_shows:
        past_shows.append([{
            'venue_id': show.id,
            'venue_name': artist.name,
            'image_link': artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        }])

    data = {
        'id': artist.id,
        'name': artist.name,
        'genres': [item.replace('{', '').replace('}', '') for item in genres],
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website': artist.website,
        'facebook_link': artist.facebook_link,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link,
        'upcoming_shows': upcoming_shows,
        'upcoming_shows_count': len(upcoming_shows),
        'past_shows_count': len(past_shows),
        'past_shows': past_shows
    }

    #artist.upcoming_shows_count = db.session.query(Show.venue_id, Show.start_time).filter(Show.artist_id == artist.id, Show.start_time >= datetime.now()).count()
    #artist.upcoming_shows = db.session.query(Show.venue_id, Show.start_time).filter(Show.artist_id == artist.id, Show.start_time >= datetime.now()).all()
    #artist.past_shows_count = db.session.query(Show.venue_id, Show.start_time).filter(Show.artist_id == artist.id, Show.start_time < datetime.now()).count()
    #artist.past_shows = db.session.query(Show.venue_id, Show.start_time).filter(Show.artist_id == artist.id, Show.start_time < datetime.now()).all()

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    print(form.name.data)
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    if request.method == 'POST':
        error = False
        form = request.form.to_dict(True)
        try:
            artist = Artist.query.get(artist_id)
            artist.genres = []
            artist.name = form['name']
            artist.genres = request.form.getlist('genres')
            artist.city = form['city']
            artist.state = form['state']
            artist.phone = form['phone']
            artist.facebook_link = form['facebook_link']
            db.session.commit()
            flash('Artist ' + request.form['name'] +
                  ' was successfully updated!')
        except:
            db.session.rollback()
            error = True
            # on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Artist ' +
                  request.form['name'] + ' could not be updated.')
            print(sys.exe_info())
        finally:
            db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    print(form.name.data)
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    if request.method == 'POST':
        error = False
        form = request.form.to_dict(True)
        try:
            venue = Venue.query.get(venue_id)
            venue.genres = []
            venue.name = form['name']
            venue.genres = request.form.getlist('genres')
            venue.city = form['city']
            venue.state = form['state']
            venue.phone = form['phone']
            venue.facebook_link = form['facebook_link']
            db.session.commit()
            flash('Venue ' + request.form['name'] + ' was successfully updated!')
        except:
            db.session.rollback()
            error = True
            # on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
            print(sys.exe_info())
        finally:
            db.session.close()

        return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    if request.method == 'POST':
        error = False
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        website = request.form['website']
        image_link = request.form['image_link']
        genres = request.form.getlist('genres')
        facebook_link = request.form['facebook_link']
        if 'seeking_venue' not in request.form:
            seeking_venue = False
        else:
            seeking_venue = request.form['seeking_venue']
        seeking_description = request.form['seeking_description']
        # TODO: modify data to be the data object returned from db insertion
        artist = Artist(name=name,
                        city=city,
                        state=state,
                        phone=phone,
                        website=website,
                        image_link=image_link,
                        genres=genres,
                        facebook_link=facebook_link,
                        seeking_venue=seeking_venue,
                        seeking_description=seeking_description)
        try:
            print(artist)
            db.session.add(artist)
            db.session.commit()
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
        except:
            db.session.rollback()
            error = True
            # on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Artist ' +
                  request.form['name'] + ' could not be listed.')
            print(sys.exe_info())
        finally:
            db.session.close()

        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    shows = Show.query.order_by(Show.start_time.desc()).all()
    for show in shows:
        venue = Venue.query.filter_by(id=show.venue_id).first_or_404()
        artist = Artist.query.filter_by(id=show.artist_id).first_or_404()
        data.extend([{
            "venue_id": venue.id,
            "venue_name": venue.name,
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        }])
    return render_template('pages/shows.html', shows=data)

    #data = []
    # order_by(Show.start_time.desc)
    #shows = Show.query.order_by(Show.start_time.desc()).all()
    # for show in shows:
    #venue = Venue.query.filter_by(id=shows.venue_id).all()
    #artist = Artist.query.filter_by(id=shows.artist_id).all()
    # data = ([{
    # "venue_id": venue.id,
    # "venue_name": venue.name,
    # "artist_id": artist.id,
    # "artist_name": artist.name,
    # "artist_image_link": artist.image_link,
    # "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    # }])


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    if request.method == 'POST':
        error = False
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']
        # TODO: modify data to be the data object returned from db insertion
        show = Show(artist_id=artist_id,
                    venue_id=venue_id,
                    start_time=start_time)
        try:
            print(show)
            db.session.add(show)
            db.session.commit()
            # on successful db insert, flash success
            flash('Show was successfully listed!')
        except:
            db.session.rollback()
            error = True
            # on unsuccessful db insert, flash an error instead.
            flash('An error occurred. The show could not be listed.')
            print(sys.exe_info())
        finally:
            db.session.close()

        return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
