#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy.inspection import inspect
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db, compare_type=True) #define migrate

# TODO: connect to a local postgresql database
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
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    genres = db.Column(db.ARRAY(db.String))

    seeking_description = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    #upcoming_shows = db.Column(db.String(120))
    #past_shows = db.Column(db.String(120))
    shows = db.relationship('Show',cascade="all, delete", backref='Venue', lazy=True)

    #upcoming_shows_count(db.Integer)
    #past_shows_count(db.Integer)

    def __repr__(self):
        return f'<Venue ID: {self.id}, name: {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Artist', lazy=True)
    #upcoming_shows_count(db.Integer)
    #past_shows_count(db.Integer)
    def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

'''class Genre(db.Model):
  __tablename__= 'Genre'
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)

  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  '''
'''
 __tablename__ = 'Show'

    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    def __repr__(self):
        return 'Show(%s, %s)' % (self.venue_id, self.artist_id)
'''

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  '''data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]'''
  #get unique areas
  areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
  data = []
  for area in areas:
    #print(area, "in area loop") --> ('Bishop', 'CA') Tuple?
    #print(area.state, area.city) --> CA Bishop
    venues = db.session.query(Venue).filter_by(state=area.state).filter_by(city=area.city).all()
    print(venues, " these are the venues for a unique area")
    venue_data = []
    for venue in venues:
      for show in venue.shows:
        print(show.start_time, "is the venue start time : ~")
      venue_data.append({
        'id':venue.id,
        'name':venue.name,
        'num_upcoming_shows': len(db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all())
      })
    data.append({
      'city':area.city,
      'state':area.state,
      'venues':venue_data
      })
  return render_template('pages/venues.html', areas=data);
  #return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST', 'GET'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '') 
  venues = db.session.query(Venue).filter(Venue.name.ilike('%'+search_term+'%')).all()
  data = []
  for venue in venues:
    data.append({
      "id" : venue.id,
      "name" : venue.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all())
    })
  response={
     "count": len(venues),
     "data": data
  }
  print(venues)
  print(search_term)
  '''response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }'''
  return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  #response contain ---> : venue.name, venue.id, venue.genres[], venue.city,
  # venue.phone, venue.website, venue.facebook_link,
  # venue.seeking_talent, venue.seeking_description, venue.image_link, 
  # venue.upcoming_shows_count, venue.past_shows_count
  # show.artist_image_link, show.artist_id, show.artist_image_link
  '''data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  } '''

  venue_data = db.session.query(Venue).filter_by(id=venue_id).all()
  print(venue_data)
  data = []
  for venue in venue_data:
    print(venue.shows)
    venue_data = []
    u_shows = db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all()
    print(u_shows)
    p_shows = db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time<datetime.now()).all()
    print(p_shows)

    upcoming_shows = []
    for show in u_shows:
      print(show.start_time) #show.start_time
      artist = db.session.query(Artist).filter(show.artist_id==Artist.id).all()[0]
      print(artist.name, "artist name") #show.aritst_name
      print(artist.image_link) #show.artist_image_link
      print(artist.id) #show.artist_id
      upcoming_shows.append({
        "artist_id": artist.id,
        "artist_image_link": artist.image_link,
        "artist_name": artist.name,
        "start_time": show.start_time
      })

    past_shows = []
    for show in p_shows:
      print(show.start_time) #show.start_time
      artist = db.session.query(Artist).filter(show.artist_id==Artist.id).all()[0]
      print(artist.name) #show.aritst_name
      print(artist.image_link) #show.artist_image_link
      print(artist.id) #show.artist_id
      past_shows.append({
        "artist_id": artist.id,
        "artist_image_link": artist.image_link,
        "artist_name": artist.name,
        "start_time": show.start_time
      })

    data.append({
      "id" : venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city":venue.city,
      "state":venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "image_link":venue.image_link,
      "upcoming_shows": upcoming_shows,
      "past_shows": past_shows,
      "past_shows_count": len(db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time<datetime.now()).all()),
      "upcoming_shows_count": len(db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all())
  })

  print(data)
  #mydata = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data[0])

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  print(form.name.data, "form.name,data")
  print(form,"form")
  
  error = False
  try:
    venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      genres = form.genres.data,
      seeking_talent = form.seeking_talent.data,
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data
    )
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

    print(venue, " is the venue")
  except:
    db.session.rollback()
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    return render_template('pages/home.html')
  else: 
    return redirect(url_for('show_venue', venue_id=venue.id))
  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue_orig(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  print(venue)
  error = false
  try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' + str(venue.name) + ' successfully deleted.')

  except():
      db.session.rollback()
      flash('An error occurred. Venue ' + str(venue.name) + ' could not be deleted.')
      error = True
  finally:
      db.session.close()
  if error:
      abort(500)
  else:
      return render_template('pages/home.html')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

@app.route('/venues/delete/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' + str(venue.name) + ' successfully deleted.')

  except():
      db.session.rollback()
      flash('An error occurred. Venue ' + str(venue.name) + ' could not be deleted.')
      error = True
  finally:
      db.session.close()
  if error:
      abort(500)
  else:
      return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  '''data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]'''

#get artists
  artists = db.session.query(Artist).all()
  #print(artists)
  data = []
  for artist in artists:
    data.append({
      'id':artist.id,
      'name':artist.name,
      })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '') 
  artists = db.session.query(Artist).filter(Artist.name.ilike('%'+search_term+'%')).all()
  artist_info = []
  for artist in artists:
    artist_info.append({
      "id" : artist.id,
      "name" : artist.name,
    })
  response={
     "count": len(artists),
     "data": artist_info
  }

  '''
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }'''
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data1={
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
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }


  artist_data = db.session.query(Artist).filter_by(id=artist_id).all()
  print(artist_data)
  data = []
  for artist in artist_data:
    print(artist.shows)
    artist_data = []
    u_shows = db.session.query(Show).filter(Show.artist_id==artist.id).filter(Show.start_time>datetime.now()).all()
    print(u_shows)
    p_shows = db.session.query(Show).filter(Show.artist_id==artist.id).filter(Show.start_time<datetime.now()).all()
    print(p_shows)

    upcoming_shows = []
    for show in u_shows:
      print(show.start_time) #show.start_time
      venue = db.session.query(Venue).filter(show.venue_id==Venue.id).all()[0]
      upcoming_shows.append({
        "venue_id": venue.id,
        "venue_image_link": venue.image_link,
        "venue_name": venue.name,
        "start_time": show.start_time
      })

    past_shows = []
    for show in p_shows:
      venue = db.session.query(Venue).filter(show.venue_id==Venue.id).all()[0]
      past_shows.append({
        "venue_id": venue.id,
        "venue_image_link": venue.image_link,
        "venue_name": venue.name,
        "start_time": show.start_time
      })

    data.append({
      "id" : artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city":artist.city,
      "state":artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link":artist.image_link,
      "upcoming_shows": upcoming_shows,
      "past_shows": past_shows,
      "past_shows_count": len(db.session.query(Show).filter(Show.artist_id==artist.id).filter(Show.start_time<datetime.now()).all()),
      "upcoming_shows_count": len(db.session.query(Show).filter(Show.artist_id==artist.id).filter(Show.start_time>datetime.now()).all())
  })

  #print(data)
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data[0])

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
#@app.route('/artists/<int:artist_id>/edit', methods=['POST'])

def edit_artist(artist_id):
  artist = db.session.query(Artist).filter(Artist.id == artist_id).all()[0]
  form = ArtistForm(obj=artist) #Populate form with artist
  print(artist)
  print(artist.name, "is the name!")
  '''artist={
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
  }'''
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  #artist = db.session.query(Artist).filter(Artist.id == artist_id).all()[0]
  artist = Artist.query.filter_by(id=artist_id).first()
  print(artist,"artist")
  form = ArtistForm(request.form)
  print(form.name.data, "form.name,data")
  print(form,"form")
  error = False
  try:
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.image_link = form.image_link.data
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Unable to update Artist : ' + request.form['name'] + '!')

    error = True
  finally:
    db.session.close()
  if error:
    abort(500)
  else: 
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = db.session.query(Venue).filter(Venue.id == venue_id).all()[0]
  form = VenueForm(obj=venue) #Populate form with venue
  print(venue)
  print(venue.name, "is the name!")

  '''venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  } '''
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.filter_by(id=venue_id).first()
  print(venue,"artist")
  form = VenueForm(request.form)
  print(form.name.data, "form.name,data")
  print(form,"form")
  error = False
  try:
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.genres = form.genres.data
    venue.seeking_talent = form.seeking_talent.data
    venue.image_link = form.image_link.data
    venue.facebook_link = form.facebook_link.data
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

  except:
    db.session.rollback()
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()
  if error:
    flash('Unable to update ' + request.form['name'] + '!')
    abort(500)

  else:
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
  # TODO: insert form data as a new Artist record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  print(form.name.data, "form.name,data")
  print(form,"form")
  
  error = False
  try:
    artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      seeking_venue = form.seeking_venue.data,
      image_link = form.image_link.data
    )
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

    print(artist, " is the artist")
  except:
    db.session.rollback()
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    return render_template('pages/home.html')
  else: 
    return redirect(url_for('show_artist', artist_id=artist.id))

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  '''data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
'''
  shows = db.session.query(Show).all()
  data = []
  for show in shows:
    artist_name = db.session.query(Artist).filter(show.artist_id==Artist.id).all()[0].name
    venue_name = db.session.query(Venue).filter(show.venue_id==Venue.id).all()[0].name
    artist_image_link = db.session.query(Artist).filter(show.artist_id==Artist.id).all()[0].image_link
    data.append({
      "venue_id" : show.venue_id,
      "artist_id": show.artist_id,
      "start_time": show.start_time,
      "artist_name": artist_name,
      "venue_name": venue_name,
      "artist_image_link": artist_image_link
  })

  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  print(form.artist_id.data, "form.artist_id.data")
  print(form,"form")
  error = False
  try:
    show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data,
    )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')

    print(show, " is the show")
  except:
    db.session.rollback()
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
    return render_template('pages/home.html')
  else:
    return redirect(url_for('shows'))
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.

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

