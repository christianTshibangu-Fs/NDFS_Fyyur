#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from os import abort
import sys
from turtle import circle
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
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
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

   # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(250))
    state = db.Column(db.String(250))
    address = db.Column(db.String(250))
    phone = db.Column(db.String(250), unique=True)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(250))
    web_link = db.Column(db.String(250))
    genres = db.Column(db.ARRAY(db.String(250)))
    search_talent = db.Column(db.Boolean(), default=True)
    search_description = db.Column(db.Text())
    shows = db.relationship('Show', backref='venue', lazy=True)

class Artiste(db.Model):
    __tablename__ = 'artistes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(250))
    state = db.Column(db.String(250))
    phone = db.Column(db.String(250), unique=True)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(250))
    web_link = db.Column(db.String(250))
    genres = db.Column(db.ARRAY(db.String(250)))
    search_venue = db.Column(db.Boolean(), default=True)
    search_description = db.Column(db.Text())
    shows = db.relationship('Show', backref='artist', lazy=True)

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artistes.id'), nullable=False)

    # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

def format_venue_shows(shows):
    new_list = []
    for show in shows:
        artist = show.artist
        new_list.append({
            'id': artist.id,
            'name': artist.name,
            'image_link': artist.image_link,
            'start_time': artist.start_time
        })
    return new_list


def format_artist_shows(shows):
    new_list = []
    for show in shows:
        venue = show.venue
        new_list.append({
            "id": venue.id,
            "name": venue.name,
            "image_link": venue.image_link,
            "start_time": venue.start_time
        })
    return new_list
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
  # TODO: DONE replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  res_result = []
  query = Venue.query.all()
  for row in query:
    city = row.city
    state = row.state
    query = db.session.query(Venue).filter(
      Venue.state == state, Venue.city == city).all()
    venues = [i for i in query]
    for i in query:
          result = {
              'city': i.city,
              'state': i.state,
              'venues': venues
            }
    res_result.append(result)
  data = [i for n, i in enumerate(
    res_result) if i not in res_result[n + 1:]]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: DONE implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 0,
    }

  search_term = request.form.get('search_term')
  venues = db.session.query(Venue).filter(Venue.name.contains(search_term)).all()
  data = []
  for venue in venues:
    # Filter upcoming shows
    upcoming_shows = Show.query.filter_by(venue_id=Venue.id).filter(
      Show.start_time > datetime.utcnow().isoformat()).all()
    res_result = {
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": upcoming_shows,
    }
    data.append(res_result)
    response = {
      "count": len(venues),
      "data": data
    }  
  return render_template('pages/search_venues.html', results=response,
   search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: DONE replace with real venue data from the venues table, using venue_id

  venue = Venue.query.filter_by(id=venue_id).first()
  data = []
  if venue:
    data = venue.__dict__
    query = db.session.query(Show).filter_by(venue_id=venue.id).all()
    shows = [i for i in query]
    for i in query:
        # Filter artist past shows
        past_shows = db.session.query(Show).filter_by(start_time=Show.start_time).filter(
            Show.start_time < datetime.utcnow().isoformat()).all()
        # Format upcoming and past shows
        upcoming_shows = db.session.query(Show).filter_by(start_time=Show.start_time).filter(
            Show.start_time > datetime.utcnow().isoformat()).all()

        data['past_shows'] = past_shows
        data['upcoming_shows'] = upcoming_shows
        data['past_shows_count'] = len(past_shows)
        data['upcoming_shows_count'] = len(upcoming_shows)

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
  form = VenueForm()
  if form.validate():
    try:
        name=request.form['name']
        city=request.form['city']
        state=request.form['state']
        address=request.form['adress']
        phone=request.form['phone']
        image_link=request.form['image_link']
        genres=request.form['genres']
        facebook_link=request.form['facebook_link']
        web_link=request.form['website_link']
        search_description=request.form['seeking_description']
        search_talents =request.form['seeking_talents']

        venue = Venue(name=name, city=city, state=state, address=address, phone=phone,
            image_link=image_link, genres=genres, facebook_link=facebook_link, web_link=web_link, search_description=search_description, search_talents=search_talents)
      

  # TODO: modify data to be the data object returned from db insertion
        db.session.add(venue)
        db.session.commit()   
        db.session.close()  
    

  # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed.')
        return render_template('pages/home.html')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except Exception as e:
          db.session.roolback()
          flash(e)
          flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
          error =True
          abort
    finally:
          db.session.close()
          return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = db.session.query(Venue).filter_by(id=venue_id).first()
        name = venue.name
        db.session.delete(venue)
        db.session.commit()
        flash('Venue, ' + name + ' successfully deleted.')

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except:
        flash('Something went wrong. ' + name + ' could not be deleted.')
        db.session.roolback()
        error =True
        abort
    finally:
        db.session.close()
        return render_template('pages/home.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
















#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: DONE =replace with real data returned from querying the database

  data = []
  res_result = []
  query = Artiste.query.all()
  for row in query:
    city = row.city
    state = row.state
    query = db.session.query(Artiste).filter(
      Artiste.state == state, Artiste.city == city).all()
    artists = [i for i in query]
    for i in query:
          result = {
            'city': i.city,
            'state': i.state,
            'artists': artists
            }
    res_result.append(result)
  data = [i for n, i in enumerate(
    res_result) if i not in res_result[n + 1:]]
  return render_template('pages/artists.html', areas=data);

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 0,
  }
  
  search_term = request.form.get("search_term")
  artists = db.session.query(Artiste).filter(Artiste.name.contains(search_term)).all()
  data = []
  for artist in artists:
        # Filter artist upcoming shows
    upcoming_shows = Show.query.filter_by(artist_id=Artiste.id).filter(
      Show.start_time > datetime.utcnow().isoformat()).all()
    res_result = {
      "id": Artiste.id,
      "name": Artiste.name,
      "num_upcoming_shows": upcoming_shows,
    }
    data.append(res_result)
    response = {
      "count": len(artists),
      "data": data
    } 
  return render_template('pages/search_artists.html', results=response, 
                    search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: DONE: replace with real artist data from the artist table, using artist_id
    
  artist = Artiste.query.filter_by(id=artist_id).first()
  data = []
  if artist:
      data = artist.__dict__
      query = db.session.query(Show).filter_by(artist_id=artist.id).all()
      for show in query:
      # Filter artist past shows
          past_shows = db.session.query(Show).filter_by(start_time=Show.start_time).filter(Show.start_time < datetime.utcnow().isoformat()).all()
      # Format upcoming and past shows
          upcoming_shows = db.session.query(Show).filter_by(start_time=Show.start_time).filter(Show.start_time > datetime.utcnow().isoformat()).all()

          data['past_shows'] = past_shows
          data['upcoming_shows'] = upcoming_shows
          data['past_shows_count'] = len(past_shows)
          data['upcoming_shows_count'] = len(upcoming_shows)

      return render_template('pages/show_artist.html', artist=data)



#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>

  artiste = db.session.query(Artiste).filter_by(id=artist_id).first()
  form.name.data = artiste.name
  form.city.data = artiste.city
  form.state.data = artiste.state
  form.phone.data = artiste.phone
  form.seeking_description.data = artiste.search_description
  form.genres.data = artiste.genres
  form.facebook_link.data = artiste.facebook_link
  form.website_link.data = artiste.web_link
  return render_template('forms/edit_artist.html', form=form, artist=artiste)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  artist = db.session.query(Artiste).filter_by(id=artist_id).first()
  if artist:
      try:
          artist.name = form.name.data,
          artist.city = form.city.data,
          artist.state = form.state.data,
          artist.phone = form.phone.data,
          artist.search_description = form.seeking_description.data,
          artist.facebook_link = form.facebook_link.data,
          artist.web_site = form.website_link.data,
          artist.genres = form.genres.data
          db.session.add(artist)
          db.session.commit()
          flash('Artist ' + request.form['name'] + ' was successfully updated.')
      except:
          flash('Something went wrong. Artist ' + request.form['name'] + ' could not be updated.')
  return redirect(url_for('pages/home.html'))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue = db.session.query(Venue).filter_by(id=venue_id).first()
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.seeking_description.data = venue.search_description
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.website_link.data = venue.web_link
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  error = False
  form = VenueForm()
  venue = db.session.query(Venue).filter_by(id=venue_id).first()
  if venue:
        try:
            venue.name = form.name.data,
            venue.city = form.city.data,
            venue.state = form.state.data,
            venue.address = form.address.data,
            venue.phone = form.phone.data,
            venue.search_description = form.seeking_description.data,
            venue.image_link = form.image_link.data,
            venue.facebook_link = form.facebook_link.data,
            venue.web_link = form.web_site.data,
            venue.genres = form.genres.data

            db.session.add(venue)
            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully updated.')
        except:
            flash('Something went wrong. Venue ' +
                  request.form['name'] + ' could not be updated.')
            error=True
            abort
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
    form = ArtistForm()
    error=False
    try:
        artist = Artiste(
          name=form.name.data,
          city=form.city.data,
          state=form.state.data,
          phone=form.phone.data,
          genres=form.genres.data,
          image_link=form.image_link,
          facebook_link=form.facebook_link.data,
          web_link=form.website.data,
          search_venues=form.seeking_venue.data,
          search_description=form.seeking_description.data,
          )

   # TODO: insert form data as a new Artiste record in the db, instead
        db.session.add(artist)
        db.session.commit()
  # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed.')
   
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/ 
    except:
        db.session.rollback()
        flash('Something went wrong. Artist '+ request.form['name'] + ' could not be listed.')
        error = True
        abort
    
    finally:
        db.session.close()
        return render_template('pages/home.html')
#
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  data = []
  query = db.session.query(Show).all()
  shows = [i for i in query]
  for i in query:
    show = {}
    show["venue_id"] = i.venue_id
    show["venue_name"] = i.venue.name
    show["artist_id"] = i.artist_id
    show["artist_name"] = i.artist.name
    show["artist_image_link"] = i.artist.image_link
    show["start_time"] = i.start_time
    data.append(show)
  return render_template('pages/shows.html', shows=data )   

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm()
    error=False
    try:
        show = Show (
                    venue_id=form.venue_id.data,
                    artist_id=form.artist_id.data,
                    start_time=form.start_time.data
                    )
        db.session.add(show)
        db.session.commit()
        flash('Show successfully listed.')

  # on successful db insert, flash success  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    
    except Exception as e :
        error=True
        abort
        flash('Something went wrong. The show could not be listed.'+' '+ e)
 
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
db.create_all()

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
