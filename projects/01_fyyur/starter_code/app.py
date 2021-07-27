#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from itertools import count
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, json, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.orm import backref
from sqlalchemy.sql.operators import startswith_op
from forms import *
from config import DatabaseURI, SQLALCHEMY_DATABASE_URI
from flask_migrate import Migrate
import datetime as dt
import sys
import os
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Venue table 
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='venue', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
      return f'<Venue ID: {self.id}, Name: {self.name}'


# Artist table
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist', lazy=True)


# Show table
class Show(db.Model):
  __tablename__ = 'Shows'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
  start_time = db.Column(db.DateTime, default=dt.datetime.now())


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

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

# Home page
@app.route('/')
def index():
  return render_template('pages/home.html')
  

#  Venues
#  ----------------------------------------------------------------
# Display list of venues
@app.route('/venues')
def venues():
  # Select unique cities and states from the database
  unique_city_states = Venue.query.distinct(Venue.city, Venue.state).all()
  data = []
  for ucs in unique_city_states:
    # Gets all the cities and states 
    unique_city_states = Venue.query.filter_by(state=ucs.state).filter_by(city=ucs.city).all()
    venue_data = []
    # Gets the venues in each city and state
    for venue in unique_city_states:
      # Append the venue id and name in the venue_data
      venue_data.append({'id': venue.id, 'name': venue.name})
      # Append the city name and the state name in the data to display only the unique cities and states 
      data.append({'city': ucs.city, 'state': ucs.state, 'venues': venue_data})

  return render_template('pages/venues.html', areas=data);

# Search for venues
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Term typed in the search bar
  search_term = request.form.get('search_term', None)
  # Gets the venues that it corresponds to the term typed
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  # Count the number of venues
  count_venues = len(venues)
  data = []
  # Show each venue by its name and id
  for v in venues:
    data.append({'id': v.id, 'name': v.name})
  response={
    "count": count_venues,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

# Show information about the venue
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # Gets the venue by its id
  venue = Venue.query.get(venue_id)
  # Gets information about the shows table
  shows = db.session.query(Show).join(Venue, Venue.id == Show.venue_id).filter(Venue.id == venue_id).all()
  past_shows = []
  upcoming_shows = []

  # Gets all the shows and it separate into past_shows and upcoming_shows by its date
  for show in shows:
    temp_show = {
      # Artist information
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time <= datetime.now():
      past_shows.append(temp_show)
    else:
      upcoming_shows.append(temp_show)

  # Venue information
  data = {
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres,
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone, 
    'website_link': venue.website_link,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows
  }

  # Shows count
  data['upcoming_shows_count'] = len(upcoming_shows)
  data['past_shows_count'] = len(past_shows)
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm(request.form)
  return render_template('forms/new_venue.html', form=form)

# Create venue 
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # Gets data from the form
  form = VenueForm(request.form)
  try:
    # Add the informations from the form into the venue
    venue = Venue(
    name=form.name.data,
    city=form.city.data,
    state=form.state.data,
    address=form.address.data, 
    phone=form.phone.data,
    genres=request.form.getlist('genres'),
    image_link=form.image_link.data,
    facebook_link=form.facebook_link.data, 
    website_link=form.website_link.data,
    seeking_talent=form.seeking_talent.data,
    seeking_description=form.seeking_description.data)

    # Add the venue into the database
    db.session.add(venue)
    db.session.commit()

    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    # Undo the changes
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + 'could not be listed!')
    print(sys.exc_info())
  finally:
    # Closes the session
    db.session.close()

  return render_template('pages/home.html')

# Venues delete button
@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  try:
    # Gets the venue that will be deleted
    venue = Venue.query.get(venue_id)
    # Delete the venue from the database
    db.session.delete(venue)
    db.session.commit()
    flash('The venue has been removed together with all of its shows.')
  except ValueError:
    # Undo the changes
    db.session.rollback()
    flash('It was not possible to delete this Venue')
  finally:
    # Close the session
    db.session.close()
  return redirect(url_for('venues'))


#  Artists
#  ----------------------------------------------------------------
# Display a list of all the artists
@app.route('/artists')
def artists():
  # Gets all the artists from the database
  artists = Artist.query.all()
  data = []
  # Append the artists information
  for artist in artists:
    data.append({
      'id': artist.id,
      'name': artist.name
    })
  return render_template('pages/artists.html', artists=data)

# Search for artist
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # Gets the term typed from the search bar
  search_term = request.form.get('search_term', None)
  # Gets all the artists who match with the term typed in the search bar
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  # Count artists
  count_artists = len(artists)
  data=[]
  for artist in artists:
    # Artist information
    data.append({
      'id': artist.id,
      'name': artist.name,
    })
  response={
    "count": count_artists,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

# Show the artist information
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # Gets all the shows who have the same artist_id as the artist
  shows = db.session.query(Show).join(Artist, Artist.id == Show.artist_id).filter(Artist.id == artist_id).all()
  # Gets the artist by its id
  artist = Artist.query.get(artist_id)
  past_shows = []
  upcoming_shows = []

  # Separate the shows in past_shows and upcoming_shows by its start_time
  for show in shows:
    # Venue information about the show
    temp_show = {
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time <= datetime.now():
      past_shows.append(temp_show)
    else:
      upcoming_shows.append(temp_show)
  data = []
  # Artist information
  data ={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website_link": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows
  }

  # Count of shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
   
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
# Edit artist
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # Gets artist who will be edited by its id
  artist = Artist.query.get(artist_id)
  # Gets all the information about the artist from the database and fill the form
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    # Change the values in the database from the values passed in the form
    form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)
    artist.name = form.name.data
    artist.genres = request.form.getlist('genres')
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.website_link = form.website_link.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    artist.image_link = form.image_link.data

    # Commit the changes
    db.session.commit()
    flash('The artist has been updated')
  except:
    # Undo the changes
    db.session.rollback()
    flash('The artist could not be updated')
  finally:
    # Close the session
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

# Edit venue
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # Gets the venue who will be edited by its id
  venue = Venue.query.get(venue_id)
  # Gets the information of the venue from the database and fill the form
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    # Update the informations in the database with what are being written on the form
    form = VenueForm(request.form)
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.genres = request.form.getlist('genres')
    venue.address = form.address.data
    venue.city = form.city.data
    venue.state = form.state.data 
    venue.phone = form.phone.data
    venue.website_link = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    venue.image_link = form.image_link.data
    # Commit the changes
    db.session.commit()
    flash('The venue has been updated')
  except:
    # Undo the changes
    db.session.rollback()
    flash('It could not update the venue')
  finally:
    # Close the session
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

# Create artist
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # Gets data from the form
  form = ArtistForm(request.form)
  try:
    # Set the informations in the artist table in the database
    artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genres=request.form.getlist('genres'),
      image_link=form.image_link.data,
      facebook_link=form.facebook_link.data,
      website_link=form.website_link.data,
      seeking_venue=form.seeking_venue.data,
      seeking_description=form.seeking_description.data,
    )
    # Add the artist in the database
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    # Undo the changes
    db.session.rollback()
    flash('Artist ' + request.form['name'] + ' coult not be listed!')
  finally:
    # Close the session
    db.session.close()
  return render_template('pages/home.html')

# Delete artist button
@app.route('/artists/<artist_id>/delete', methods=['POST'])
def delete_artist(artist_id):
  try:
    # Gets the artist who will be deleted by its id
    artist = Artist.query.get(artist_id)
    # Delete artist from the database
    db.session.delete(artist)
    db.session.commit()
    flash('The Artist has been removed together with all of its shows.')
    #return render_template('/artists')
  except ValueError:
    # Undo the changes
    db.session.rollback()
    flash('It was not possible to delete this Artist')
  finally:
    # Close the session
    db.session.close()
  return redirect(url_for('artists'))


#  Shows
#  ----------------------------------------------------------------
# Displays all the shows
@app.route('/shows')
def shows():
  # Gets all the shows who the artist_id and the venue_id match
  shows = db.session.query(Show).join(Artist, Artist.id == Show.artist_id).join(Venue, Venue.id == Show.venue_id).filter(
    Show.venue_id == Venue.id,
    Show.artist_id == Artist.id
  ).all()

  data = []
  # Show information
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d, %H:%H")
    })
    
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

# Create show
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    # Gets data from the form
    form = ShowForm(request.form)
    # Sets the show parameters with data from the form
    show = Show(
      artist_id=form.artist_id.data,
      venue_id=form.venue_id.data,
      start_time=form.start_time.data
    )
    # Add show in the database
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    # Undo the changes
    db.session.rollback()
    flash('Show could not be listed!')
  finally:
    # Close session
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
